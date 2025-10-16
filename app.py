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
    return "Welcome to the DevOps Demo App!! Version 8"

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def add_task():
    new_task = request.get_json()
    new_task["id"] = len(tasks) + 1
    tasks.append(new_task)
    return jsonify(new_task), 201

#
#
WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "supersecret")

@app.route('/gitpull', methods=['POST'])
def gitpull():
    # --- Get whichever signature GitHub sent ---
    signature_header = request.headers.get('X-Hub-Signature-256') or request.headers.get('X-Hub-Signature')
    if not signature_header:
        abort(403)

    try:
        algo, signature = signature_header.split('=')
    except ValueError:
        abort(403)

    if algo not in ('sha256', 'sha1'):
        abort(403)

    # --- Compute HMAC with same algorithm ---
    digestmod = hashlib.sha256 if algo == 'sha256' else hashlib.sha1
    mac = hmac.new(WEBHOOK_SECRET.encode(), msg=request.data, digestmod=digestmod)

    # --- Compare signatures safely ---
    if not hmac.compare_digest(mac.hexdigest(), signature):
        print("Signature mismatch! Computed:", mac.hexdigest())
        abort(403)

    # --- Pull repo ---
    try:
        repo_path = '/home/mikedorin/CICD_Python_Anywhere'
        subprocess.run(['git', '-C', repo_path, 'pull'], check=True)
        return '✅ Code updated via git pull.', 200
    except subprocess.CalledProcessError as e:
        return f'❌ Git pull failed: {e}', 500



if __name__ == '__main__':
    app.run()