student = {"name" : "Raviraj",
        "age" : "22",
        "country" : "India"}
print(student['name'])
print(student.get('age'))

student['course'] = "AI/ML"
student['age']="23"

print(student)

student.pop('age')
del student['country']
print(student)