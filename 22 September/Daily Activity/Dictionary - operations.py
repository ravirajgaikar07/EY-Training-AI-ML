student = {"name" : "Raviraj",
        "age" : "22",
        "country" : "India"}

student['course'] = "AI/ML"
student['age']="23"

print(student)

student.pop('age')
del student['country']
print(student)