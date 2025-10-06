import json
student = {
    "name" : "Rahul",
    "age" : 21,
    "courses" : ["AI","ML"],
    "marks" : {"AI":85, "ML":82}
}

with open ("students.json","w") as f:
    json.dump(student,f,indent=4)

with open ("students.json","r") as f:
    data=json.load(f)

print(data["name"])
print(data["marks"]["ML"])
