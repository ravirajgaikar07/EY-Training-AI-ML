from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class Employee(BaseModel):
    id: int
    name: str
    department: str
    salary: float

employees = [
    {"id":1, "name":"Rahul", "department":"AI", "salary":50000}
]

app=FastAPI()

@app.get("/employees")
def get_all():
    return employees

@app.get("/employees/{emp_id}")
def get_employee(emp_id: int):
    for emp in employees:
        if emp["id"]==emp_id:
            return emp
    raise HTTPException(status_code=404, detail="employee not found")

@app.post("/employees",status_code=201)
def add_employee(employee: Employee):
    employees.append(employee.model_dump())
    return employee

@app.put("/employees/{emp_id}")
def update_employee(emp_id:int, employee:Employee):
    for i, emp in enumerate(employees):
        if emp["id"]==emp_id:
            employees[i]=employee.model_dump()
            return {"message" : "Employee updated", "employee": employee}
    raise HTTPException(status_code=404, detail="employee not found")

@app.delete("/employees/{emp_id}")
def delete_employee(emp_id:int):
    for i, emp in enumerate(employees):
        if emp["id"]==emp_id:
            del employees[i]
            return {"message" : "Employee deleted"}
    raise HTTPException(status_code=404, detail="employee not found")