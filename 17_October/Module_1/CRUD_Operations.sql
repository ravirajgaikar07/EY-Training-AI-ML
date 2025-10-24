CREATE DATABASE hospital;
USE hospital;

CREATE TABLE patients(
	PatientID VARCHAR(10) PRIMARY KEY,
    Name VARCHAR(50),
    Age INT,
    Gender VARCHAR(10),
    `Condition` VARCHAR(50)
    );
    
CREATE TABLE doctors(
	DoctorID VARCHAR(10) PRIMARY KEY,
    Name VARCHAR(50),
    Specialization VARCHAR(50)
);

INSERT INTO patients(PatientID,Name,Age,`Condition`)
VALUES
('P001','Neha',32,'Fever'),
('P002','Arjun',45,'Diabetes'),
('P003','Sophia',28,'Hypertension'),
('P004','Ravi',52,'Asthma'),
('P005','Meena',38,'Arthritis');

INSERT INTO doctors(DoctorID,Name,Specialization)
VALUES
('D101','Dr. Patel','General Physician'),
('D102','Dr. Khan','Endocrinologist'),
('D103','Dr. Verma','Cardiologist'),
('D104','Dr. Rao','Pulmonologist');

-- Add a new patient record
INSERT INTO patients VALUES
('P006','Prakash',35,'M','Diabetes');

-- Update a doctor’s specialization
UPDATE doctors
SET Specialization='Neurologist' where DoctorID='D102';

-- Delete a patient
DELETE from patients
WHERE PatientID='P006';

-- Fetch all patients above age 40
SELECT * FROM patients
WHERE Age>40;
