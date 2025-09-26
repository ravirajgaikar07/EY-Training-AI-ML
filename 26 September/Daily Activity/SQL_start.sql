CREATE DATABASE schooldb;
USE schooldb;

CREATE TABLE Students (
	id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    age INT,
    course VARCHAR(50),
    marks INT
    );

INSERT INTO students(name,age,course,marks)
VALUES 
("Rahul",21,"AI",85),
("Priya","22","BI",82),
("Ratan","23","ML",90);

Select * from students;
Select name,marks from students;
Select * from students where marks>80;

UPDATE students
SET age=22, course="Advanced AI"
where id=1;

DELETE from students where id=3;
