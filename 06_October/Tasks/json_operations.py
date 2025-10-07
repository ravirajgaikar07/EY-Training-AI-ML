import json
import logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logging.info("Logging started")
logging.info("Data Creation")
students=[
    {"name": "Rahul", "age": 21, "course": "AI", "marks": 85},
    {"name": "Priya", "age": 22, "course": "ML", "marks": 90}
]
logging.info("Saving Data in JSON file")
with open("students.json","w") as f:
    json.dump(students,f)
logging.info("Data Saved in JSON file")

logging.info("Loading Data in Memory")
with open("students.json","r") as f:
    data=json.load(f)

logging.info("Printing names of students")
for i in range(len(data)):
    print(data[i]["name"])

logging.info("Adding new data")
new_data={ "name" : "Arjun" , "age" : 20, "course" : "Data Science" , "marks" : 78}
data.append(new_data)
with open("students.json","w") as f:
    json.dump(data,f,indent=4)
logging.info("New Data Added")
