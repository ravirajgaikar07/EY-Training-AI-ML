from pydantic import BaseModel

class Student(BaseModel):
    name:str
    age: int
    email:str
    is_active : bool = True

# data = {"name":"Bob", "age":"twenty", "email":"abc@example.com"} #invalid data
data = {"name":"Bob", "age":20, "email":"abc@example.com"} # valid data
student=Student(**data)
print(student)
print(student.name)