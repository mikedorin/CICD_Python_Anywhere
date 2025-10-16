from flask import Flask, jsonify, request

app = Flask(__name__)

tasks = [
    {"id": 1, "task": "Learn DevOps", "done": False},
    {"id": 2, "task": "Deploy to PythonAnywhere", "done": False}
]

@app.route('/')
def home():
    return "Welcome to the DevOps Demo App!"

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def add_task():
    new_task = request.get_json()
    new_task["id"] = len(tasks) + 1
    tasks.append(new_task)
    return jsonify(new_task), 201

if __name__ == '__main__':
    app.run()