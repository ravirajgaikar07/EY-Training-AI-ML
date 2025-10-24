from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import mysql.connector
from mysql.connector import Error

app = FastAPI()

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root@123',
    'database': 'hospital'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {e}")

class Patient(BaseModel):
    PatientID: Optional[str]  # For POST only
    Name: str
    Age: int
    Gender: Optional[str] = None
    Condition: Optional[str] = None

class Doctor(BaseModel):
    DoctorID: Optional[str]  # For POST only
    Name: str
    Specialization: Optional[str] = None

# PATIENTS

@app.get("/patients", response_model=List[Patient])
def get_patients():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patients")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

@app.post("/patients")
def add_patient(patient: Patient):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
        INSERT INTO patients (PatientID, Name, Age, Gender, `Condition`)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (patient.PatientID, patient.Name, patient.Age, patient.Gender, patient.Condition))
        conn.commit()
    except Error as e:
        raise HTTPException(status_code=400, detail="Patient with this ID already exists")
    finally:
        cursor.close()
        conn.close()
    return {"message": "Patient added successfully!"}

@app.put("/patients/{patient_id}")
def update_patient(patient_id: str, patient: Patient):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    UPDATE patients
    SET Name = %s, Age = %s, Gender = %s, `Condition` = %s
    WHERE PatientID = %s
    """
    cursor.execute(query, (patient.Name, patient.Age, patient.Gender, patient.Condition, patient_id))
    conn.commit()
    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Patient not found")
    cursor.close()
    conn.close()
    return {"message": "Patient updated successfully!"}

@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patients WHERE PatientID = %s", (patient_id,))
    conn.commit()
    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Patient not found")
    cursor.close()
    conn.close()
    return {"message": "Patient deleted successfully!"}

# DOCTORS

@app.get("/doctors", response_model=List[Doctor])
def get_doctors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM doctors")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

@app.post("/doctors")
def add_doctor(doctor: Doctor):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
        INSERT INTO doctors (DoctorID, Name, Specialization)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (doctor.DoctorID, doctor.Name, doctor.Specialization))
        conn.commit()
    except Error as e:
        raise HTTPException(status_code=400, detail="Doctor with this ID already exists")
    finally:
        cursor.close()
        conn.close()
    return {"message": "Doctor added successfully!"}

@app.put("/doctors/{doctor_id}")
def update_doctor(doctor_id: str, doctor: Doctor):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    UPDATE doctors
    SET Name = %s, Specialization = %s
    WHERE DoctorID = %s
    """
    cursor.execute(query, (doctor.Name, doctor.Specialization, doctor_id))
    conn.commit()
    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Doctor not found")
    cursor.close()
    conn.close()
    return {"message": "Doctor updated successfully!"}

@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM doctors WHERE DoctorID = %s", (doctor_id,))
    conn.commit()
    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Doctor not found")
    cursor.close()
    conn.close()
    return {"message": "Doctor deleted successfully!"}



# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from typing import List
# import logging
#
# logging.basicConfig(
#     filename="app.log",
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )
#
# logger = logging.getLogger(__name__)
#
# app = FastAPI()
#
# class Patient(BaseModel):
#     PatientID: str
#     Name: str
#     Age: int
#     Gender: str
#     Condition: str
#
# class Doctor(BaseModel):
#     DoctorID: str
#     Name: str
#     Specialization: str
#
# patients_db = {
#     "P001": Patient(PatientID="P001", Name="Neha", Age=32, Gender="Female", Condition="Fever"),
#     "P002": Patient(PatientID="P002", Name="Arjun", Age=45, Gender="Male", Condition="Diabetes"),
#     "P003": Patient(PatientID="P003", Name="Sophia", Age=28, Gender="Female", Condition="Hypertension"),
#     "P004": Patient(PatientID="P004", Name="Ravi", Age=52, Gender="Male", Condition="Asthma"),
#     "P005": Patient(PatientID="P005", Name="Meena", Age=38, Gender="Female", Condition="Arthritis"),
# }
#
# doctors_db = {
#     "D101": Doctor(DoctorID="D101", Name="Dr. Patel", Specialization="General Physician"),
#     "D102": Doctor(DoctorID="D102", Name="Dr. Khan", Specialization="Endocrinologist"),
#     "D103": Doctor(DoctorID="D103", Name="Dr. Verma", Specialization="Cardiologist"),
#     "D104": Doctor(DoctorID="D104", Name="Dr. Rao", Specialization="Pulmonologist"),
# }
#
# @app.get("/patients", response_model=List[Patient])
# def get_patients():
#     logger.info("Fetched all patients")
#     return list(patients_db.values())
#
# @app.post("/patients")
# def add_patient(patient: Patient):
#     if patient.PatientID in patients_db:
#         logger.warning(f"Attempt to add existing patient ID: {patient.PatientID}")
#         raise HTTPException(status_code=400, detail="Patient already exists")
#     patients_db[patient.PatientID] = patient
#     logger.info(f"Added new patient: {patient.PatientID} - {patient.Name}")
#     return {"message": "Patient added successfully", "patient": patient}
#
# @app.put("/patients/{patient_id}")
# def update_patient(patient_id: str, updated_patient: Patient):
#     if patient_id not in patients_db:
#         logger.error(f"Update failed: Patient ID not found - {patient_id}")
#         raise HTTPException(status_code=404, detail="Patient not found")
#     patients_db[patient_id] = updated_patient
#     logger.info(f"Updated patient: {patient_id}")
#     return {"message": "Patient updated successfully", "updated data": updated_patient}
#
# @app.delete("/patients/{patient_id}")
# def delete_patient(patient_id: str):
#     if patient_id not in patients_db:
#         logger.error(f"Delete failed: Patient ID not found - {patient_id}")
#         raise HTTPException(status_code=404, detail="Patient not found")
#     del patients_db[patient_id]
#     logger.info(f"Deleted patient: {patient_id}")
#     return {"message": "Patient deleted successfully"}
#
# @app.get("/doctors", response_model=List[Doctor])
# def get_doctors():
#     logger.info("Fetched all doctors")
#     return list(doctors_db.values())
#
# @app.post("/doctors")
# def add_doctor(doctor: Doctor):
#     if doctor.DoctorID in doctors_db:
#         logger.warning(f"Attempt to add existing doctor ID: {doctor.DoctorID}")
#         raise HTTPException(status_code=400, detail="Doctor already exists")
#     doctors_db[doctor.DoctorID] = doctor
#     logger.info(f"Added new doctor: {doctor.DoctorID} - {doctor.Name}")
#     return {"message": "Doctor added successfully", "doctor": doctor}
#
# @app.put("/doctors/{doctor_id}")
# def update_doctor(doctor_id: str, updated_doctor: Doctor):
#     if doctor_id not in doctors_db:
#         logger.error(f"Update failed: Doctor ID not found - {doctor_id}")
#         raise HTTPException(status_code=404, detail="Doctor not found")
#     doctors_db[doctor_id] = updated_doctor
#     logger.info(f"Updated doctor: {doctor_id}")
#     return {"message": "Doctor updated successfully", "doctor": updated_doctor}
#
# @app.delete("/doctors/{doctor_id}")
# def delete_doctor(doctor_id: str):
#     if doctor_id not in doctors_db:
#         logger.error(f"Delete failed: Doctor ID not found - {doctor_id}")
#         raise HTTPException(status_code=404, detail="Doctor not found")
#     del doctors_db[doctor_id]
#     logger.info(f"Deleted doctor: {doctor_id}")
#     return {"message": "Doctor deleted successfully"}