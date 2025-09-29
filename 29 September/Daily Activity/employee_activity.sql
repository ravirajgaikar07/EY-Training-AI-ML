CREATE DATABASE CompanyDB;
USE CompanyDB;

CREATE TABLE Departments(
	dept_id INT PRIMARY KEY AUTO_INCREMENT,
    dept_name VARCHAR(50) NOT NULL
);

CREATE TABLE Employees(
	emp_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50),
    age INT,
    salary DECIMAL(10,2),
    dept_id INT,
    FOREIGN KEY(dept_id) REFERENCES Departments(dept_id)
);

INSERT INTO Departments(dept_name) VALUES
('IT'),
('HR'),
('Finance'),
('Sales');


INSERT INTO Employees (name, age, salary, dept_id) VALUES

('Rahul', 28, 55000, 1),   -- IT

('Priya', 32, 60000, 2),   -- HR

('Arjun', 25, 48000, 3),   -- Finance

('Neha', 30, 70000, 1),    -- IT

('Vikram', 35, 65000, 4);  -- Sales

ALTER TABLE Employees DROP FOREIGN KEY employees_ibfk_1;

TRUNCATE TABLE Employees;
TRUNCATE TABLE Departments;

INSERT INTO Departments (dept_name) VALUES
('IT'),         -- id = 1
('HR'),         -- id = 2
('Finance'),    -- id = 3
('Sales'),      -- id = 4
('Marketing');  -- id = 5  


INSERT INTO Employees (name, age, salary, dept_id) VALUES
('Rahul', 28, 55000, 1),   -- IT
('Priya', 32, 60000, 2),   -- HR
('Arjun', 25, 48000, NULL),-- 
('Neha', 30, 70000, 1),    -- IT
('Vikram', 35, 65000, 4);  -- Sales

 
SELECT e.name, e.salary, d.dept_name
FROM Employees e
INNER JOIN Departments d
ON e.dept_id=d.dept_id;

SELECT e.name, e.salary, d.dept_name
FROM Employees e
LEFT JOIN Departments d
ON e.dept_id=d.dept_id;

SELECT e.name, e.salary, d.dept_name
FROM Employees e
RIGHT JOIN Departments d
ON e.dept_id=d.dept_id;


SELECT e.name, e.salary, d.dept_name
FROM Employees e
LEFT JOIN Departments d
ON e.dept_id=d.dept_id

UNION

SELECT e.name, e.salary, d.dept_name
FROM Employees e
RIGHT JOIN Departments d
ON e.dept_id=d.dept_id;