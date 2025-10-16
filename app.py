from flask import Flask, jsonify, request, abort
import subprocess
import hmac
import hashlib
import os

app = Flask(__name__)

tasks = [
    {"id": 1, "task": "Learn DevOps", "done": False},
    {"id": 2, "task": "Deploy to PythonAnywhere", "done": False}
]

@app.route('/')
def home():
    return "Welcome to the DevOps Demo App!! Version 5"

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def add_task():
    new_task = request.get_json()
    new_task["id"] = len(tasks) + 1
    tasks.append(new_task)
    return jsonify(new_task), 201


WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "supersecret")

@app.route('/gitpull', methods=['POST'])
def gitpull():
    # --- Validate GitHub HMAC signature ---
    signature_header = request.headers.get('X-Hub-Signature-256')
    if not signature_header:
        abort(403)

    try:
        sha_name, signature = signature_header.split('=')
    except ValueError:
        abort(403)

    if sha_name != 'sha256':
        abort(403)

    mac = hmac.new(WEBHOOK_SECRET.encode(), msg=request.data, digestmod=hashlib.sha256)
    if not hmac.compare_digest(mac.hexdigest(), signature):
        abort(403)

    # --- Run git pull and reload web app ---
    try:
        repo_path = '/home/mikedorin/CICD_Python_Anywhere'

        # Pull the latest code
        subprocess.run(['git', '-C', repo_path, 'pull'], check=True)

        # Reload the PythonAnywhere web app
        subprocess.run(['/usr/local/bin/pa_reload_webapp', 'mikedorin.pythonanywhere.com'], check=True)

        return '✅ Update and reload triggered successfully.', 200

    except subprocess.CalledProcessError as e:
        return f'❌ Subprocess error: {e}', 500
    except Exception as e:
        return f'⚠️ Unexpected error: {e}', 500


if __name__ == '__main__':
    app.run()