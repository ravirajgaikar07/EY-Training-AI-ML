class Student:
    def __init__(self,name,age,email):
        self.name=name
        self.age=age
        self.email=email

data = {"name":"Bob", "age":"twenty", "email":"abc@example.com"}

student=Student(**data)
print(student.name)