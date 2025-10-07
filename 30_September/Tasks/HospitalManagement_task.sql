CREATE DATABASE Hospital_Management;
USE Hospital_Management;

CREATE TABLE Patients(
	patient_id INT PRIMARY KEY,
	name VARCHAR(50),
	age INT,
	gender CHAR(1),
	city VARCHAR(50)
);

CREATE TABLE Doctors(
	doctor_id INT PRIMARY KEY,
	name VARCHAR(50),
	specialization VARCHAR(50),
	experience INT
);

CREATE TABLE Appointments(
appointment_id INT PRIMARY KEY,
patient_id INT,
doctor_id INT,
appointment_date DATE,
status VARCHAR(20),
FOREIGN KEY(patient_id) REFERENCES Patients(patient_id),
FOREIGN KEY(doctor_id) REFERENCES Doctors(doctor_id)
);


CREATE TABLE MedicalRecords(
	record_id INT PRIMARY KEY,
	patient_id INT,
	doctor_id INT,
	diagnosis VARCHAR(100),
	treatment VARCHAR(100),
	date DATE,
    FOREIGN KEY(patient_id) REFERENCES Patients(patient_id),
    FOREIGN KEY(doctor_id) REFERENCES Doctors(doctor_id)
);

CREATE TABLE Billing(
	bill_id INT PRIMARY KEY,
	patient_id INT,
	amount DECIMAL(10,2),
	bill_date DATE,
	status VARCHAR(20),
    FOREIGN KEY(patient_id) REFERENCES Patients(patient_id)
);

INSERT INTO Patients VALUES
(101, "Rahul", 19, 'M', 'Pune'),
(102, "Vivek", 20, 'M', 'Mumbai'),
(103, "Avantika", 21, 'F', 'Thane'),
(104, "John", 23, 'M', 'Nashik'),
(105, "Shraddha", 22, 'F', 'Pune'),
(106, "Jasmin", 25, 'F', 'Mumbai'),
(107, "Bob", 35, 'M', 'Nagpur'),
(108, "Ovi", 60, 'F', 'Dhule'),
(109, "Chetan", 35, 'M', 'PCMC'),
(110, "Vinay", 20, 'M', 'Nashik');

INSERT INTO Doctors VALUES
(01,"Vivek Khanna","Cardiology",25),
(02,"Raunak Khatri","Cardiology",23),
(03,"Ashwini Mittal","Neurology",15),
(04,"Rajesh Pawar","Orthopedics",17),
(05,"Mohit Sharma","Pediatrics",12);

INSERT INTO Appointments VALUES
  (1001, 101, 01, '2025-10-01', 'Scheduled'),
  (1002, 102, 02, '2025-10-02', 'Completed'),
  (1003, 103, 03, '2025-10-03', 'Completed'),
  (1004, 104, 04, '2025-10-04', 'Completed'),
  (1005, 105, 05, '2025-10-05', 'Completed'),
  (1006, 106, 01, '2025-10-06', 'Completed'),
  (1007, 107, 02, '2025-10-07', 'Completed'),
  (1008, 108, 03, '2025-10-08', 'Scheduled'),
  (1009, 109, 04, '2025-10-09', 'Completed'),
  (1010, 110, 05, '2025-10-10', 'Scheduled');
  
INSERT INTO MedicalRecords VALUES
  (2001, 101, 01, 'Hypertension', 'Lifestyle changes and medication', '2025-09-01'),
  (2002, 102, 02, 'Arrhythmia', 'Beta blockers and ECG monitoring', '2025-09-02'),
  (2003, 103, 03, 'Migraine', 'Pain relievers and rest', '2025-09-03'),
  (2004, 104, 04, 'Fractured wrist', 'Casting and physiotherapy', '2025-09-04'),
  (2005, 105, 05, 'Flu', 'Antiviral medication and fluids', '2025-09-05'),
  (2006, 106, 01, 'High cholesterol', 'Statins and dietary changes', '2025-09-06'),
  (2007, 107, 02, 'Heart murmur', 'Echocardiogram and monitoring', '2025-09-07'),
  (2008, 108, 03, 'Epilepsy', 'Anticonvulsants and regular checkups', '2025-09-08'),
  (2009, 109, 04, 'Knee pain', 'MRI and physiotherapy', '2025-09-09'),
  (2010, 110, 05, 'Chickenpox', 'Antihistamines and calamine lotion', '2025-09-10');
  
INSERT INTO Billing VALUES
  (3001, 101, 1500.00, '2025-09-01', 'Paid'),
  (3002, 102, 2000.00, '2025-09-02', 'Unpaid'),
  (3003, 103, 1750.50, '2025-09-03', 'Paid'),
  (3004, 104, 2200.75, '2025-09-04', 'Unpaid'),
  (3005, 105, 1300.00, '2025-09-05', 'Paid'),
  (3006, 106, 1600.25, '2025-09-06', 'Unpaid'),
  (3007, 107, 2100.00, '2025-09-07', 'Paid'),
  (3008, 108, 1950.00, '2025-09-08', 'Unpaid'),
  (3009, 109, 1800.00, '2025-09-09', 'Paid'),
  (3010, 110, 1400.00, '2025-09-10', 'Unpaid');


-- Basic Queries
-- 1. List all patients assigned to a cardiologist.
SELECT p.name, p.age, p.city
from Patients p
JOIN MedicalRecords m
ON p.patient_id=m.patient_id
JOIN Doctors d
ON d.doctor_id=m.doctor_id
WHERE d.specialization='Cardiology';

-- 2. Find all appointments for a given doctor.
SELECT d.name, GROUP_CONCAT(a.appointment_id) as appointment_ids, GROUP_CONCAT(a.patient_id) as patient_ids, GROUP_CONCAT(a.appointment_date) as appointment_dates, GROUP_CONCAT(a.status) as status
FROM Appointments a
JOIN Doctors d
ON d.doctor_id=a.doctor_id
GROUP BY(a.doctor_id);

-- 3. Show unpaid bills of patients.
Select b.bill_id, b.patient_id, b.amount, b.status
FROM Billing b
WHERE b.status='Unpaid';

-- Stored Procedures
-- 4. Procedure: GetPatientHistory(patient_id) → returns all visits, diagnoses, and treatments for a patient.
DELIMITER $$

CREATE PROCEDURE GetPatientHistory(IN id INT)
BEGIN
	SELECT doctor_id, diagnosis, treatment
	FROM MedicalRecords
	WHERE patient_id=id;
END $$

DELIMITER ;
CALL GetPatientHistory(105);
-- 5. Procedure: GetDoctorAppointments(doctor_id) → returns all appointments for a doctor.
DELIMITER $$

CREATE PROCEDURE GetDoctorAppointments(IN id INT)
BEGIN
	SELECT a.appointment_id, a.patient_id,a.appointment_date
	FROM Appointments a
    WHERE a.doctor_id=id AND a.status='Scheduled';
END $$

DELIMITER ;
CALL GetDoctorAppointments(01);
