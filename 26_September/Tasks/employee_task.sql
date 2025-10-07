CREATE TABLE Employees (
	id INT AUTO_INCREMENT PRIMARY KEY,
	name VARCHAR(50) NOT NULL,
	age INT,
	department VARCHAR(50),
	salary DECIMAL(10,2)
);

INSERT INTO employees(name,age,department,salary)
VALUES
("Chetan",22,"AI",70000000.00),
("Rahul",25,"ML",90000000.00),
("Priya",21,"HR",65000000.00);

Select * from employees;
Select name from employees where age>22;

Update employees
set salary=85000000
where id=2;

delete from employees where id=1;