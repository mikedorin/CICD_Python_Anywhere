import json
from app import app

def test_home_route():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome" in response.data

def test_get_tasks():
    client = app.test_client()
    response = client.get('/tasks')
    data = json.loads(response.data)
    assert type(data) is list
    assert "task" in data[0]

def test_add_task():
    client = app.test_client()
    new_task = {"task": "Write CI/CD workflow", "done": False}
    response = client.post('/tasks', json=new_task)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["task"] == "Write CI/CD workflow"