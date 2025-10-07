from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel

class Employee(BaseModel):
    id: int
    name: str
    department: str
    salary: float

data = [
    {"id":1, "name":"Rahul", "department":"AI", "salary":50000},
    {"id":2, "name":"Priya", "department":"ML", "salary":45000},
    {"id":3, "name":"Bob", "department":"DS", "salary":40000},
]

app=FastAPI()

@app.get("/employees/count")
def count_employees():
    return {"Number of Employees": len(data)}

@app.get("/employees")
def get_all_employees():
    return data

@app.get("/employees/{emp_id}")
def get_employee(emp_id: int):
    for i, emp in enumerate(data):
        if emp["id"]==emp_id:
            return emp
    raise HTTPException(status_code=404, detail="employee not found")

@app.post("/employees")
def add_employee(employee: Employee):
    for emp in data:
        if emp["id"]==employee.id:
            return {"message":"employee already exists"}
    data.append(employee.dict())
    return {"message" : "Employee added", "employee": employee}

@app.put("/employees/{emp_id}")
def update_employee(emp_id:int, employee:Employee):
    for i, emp in enumerate(data):
        if emp["id"]==emp_id:
            data[i]=employee.dict()
            return {"message" : "Employee updated", "employee": employee}
    raise HTTPException(status_code=404, detail="employee not found")

@app.delete("/employees/{emp_id}")
def delete_employee(emp_id:int):
    for i, emp in enumerate(data):
        if emp["id"]==emp_id:
            del data[i]
            return {"message" : "Employee deleted"}
    raise HTTPException(status_code=404, detail="employee not found")
