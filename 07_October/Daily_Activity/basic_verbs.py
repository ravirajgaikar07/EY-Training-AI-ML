from fastapi import FastAPI

app=FastAPI()

@app.get("/students")
def get_students():
    return {"This is a GET request"}

@app.post("/students")
def create_student():
    return {"This is a POST request"}

@app.put("/students")
def update_students():
    return {"This is a PUT request"}

@app.delete("/students")
def delete_student():
    return {"This is a DELETE request"}
