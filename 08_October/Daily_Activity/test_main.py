from fastapi.testclient import TestClient
from main import app

client=TestClient(app)

def test_get_all_employees():
    response = client.get("/employees")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_add_employee():
    new_app = {
        "id":2,
        "name":"Neha Verma",
        "department":"IT",
        "salary":50000
    }
    response = client.post("/employees", json=new_app)
    assert response.status_code == 201
    assert response.json()["name"] == "Neha Verma"

def test_get_employee_by_id():
    response = client.get("/employees/1")
    assert response.status_code==200
    assert response.json()["name"] == "Rahul"

def test_get_employee_not_found():
    response = client.get("/employees/999")
    assert response.status_code==404
    assert response.json()["detail"]=="employee not found"

def test_update_employee():
    data = {
        "id": 1,
        "name": "Prakash Verma",
        "department": "Tax",
        "salary": 50000
    }
    response = client.put("/employees/1", json=data)
    assert response.status_code==200
    assert response.json()["message"] == "Employee updated"

def test_delete_employee():
    response = client.delete("/employees/2")
    assert response.status_code==200
    assert response.json()["message"] == "Employee deleted"