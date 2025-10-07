CREATE DATABASE UniversityDB;
USE UniversityDB;

-- Students Table
CREATE TABLE Students (
student_id INT PRIMARY KEY,
name VARCHAR(50),
city VARCHAR(50)
);
-- Courses Table
CREATE TABLE Courses (
course_id INT PRIMARY KEY,
course_name VARCHAR(50),
credits INT
);
-- Enrollments Table
CREATE TABLE Enrollments (
enroll_id INT PRIMARY KEY,
student_id INT,
course_id INT,
grade CHAR(2),
FOREIGN KEY (student_id) REFERENCES Students(student_id),
FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);
-- Insert Students
INSERT INTO Students VALUES
(1, 'Rahul', 'Mumbai'),
(2, 'Priya', 'Delhi'),
(3, 'Arjun', 'Bengaluru'),
(4, 'Neha', 'Hyderabad'),
(5, 'Vikram', 'Chennai');
-- Insert Courses
INSERT INTO Courses VALUES
(101, 'Mathematics', 4),
(102, 'Computer Science', 3),
(103, 'Economics', 2),
(104, 'History', 3);
-- Insert Enrollments
INSERT INTO Enrollments VALUES
(1, 1, 101, 'A'),
(2, 1, 102, 'B'),
(3, 2, 103, 'A'),
(4, 3, 101, 'C'),
(5, 4, 102, 'B'),
(6, 5, 104, 'A');

-- Level 1: Single Table
-- List all students
DELIMITER $$
CREATE PROCEDURE ListAllStudents()
BEGIN
SELECT * from Students;
END $$

DELIMITER ;
CALL ListAllStudents();

-- List all courses
DELIMITER $$
CREATE PROCEDURE ListAllCourses()
BEGIN
SELECT * from Courses;
END $$

DELIMITER ;
CALL ListAllCourses();

-- List all students from a given city
DELIMITER $$
CREATE PROCEDURE ListStudentFromCity(IN city VARCHAR(50))
BEGIN
SELECT * from Students s
WHERE s.city=city;
END $$

DELIMITER ;
CALL ListStudentFromCity('Mumbai');

-- Level 2: Two-Table Joins
-- List students with their enrolled courses.
DELIMITER $$
CREATE PROCEDURE ListStudentAndCourses()
BEGIN
SELECT s.name, GROUP_CONCAT(c.course_name SEPARATOR ', ') AS courses
from Students s
JOIN Enrollments e
ON e.student_id=s.student_id
JOIN Courses c
ON e.course_id=c.course_id
GROUP BY s.name;
END $$

DELIMITER ;
CALL ListStudentAndCourses();

-- list all students enrolled in a given course
DELIMITER $$
CREATE PROCEDURE ListStudentsByCourse(IN course_id INT)
BEGIN
SELECT s.name, c.course_name
FROM Students s
JOIN Enrollments e
ON s.student_id=e.student_id
JOIN Courses c
ON c.course_id=e.course_id
WHERE e.course_id=course_id;
END $$

DELIMITER ;
CALL ListStudentsByCourse(101);

-- count the number of students in each course.
DELIMITER $$
CREATE PROCEDURE CountByCourse()
BEGIN
SELECT c.course_name, COUNT(s.student_id) AS total_count
from Students s
JOIN Enrollments e
ON e.student_id=s.student_id
JOIN Courses c
ON e.course_id=c.course_id
GROUP BY c.course_name;
END $$

DELIMITER ;
CALL CountByCourse();

-- Level 3: Three-Table Joins
-- list students with course names and grades.
DELIMITER $$
CREATE PROCEDURE StudentWithCourseAndGrade()
BEGIN
SELECT s.name, c.course_name, e.grade
from Students s
JOIN Enrollments e
ON e.student_id=s.student_id
JOIN Courses c
ON e.course_id=c.course_id;
END $$

DELIMITER ;
CALL StudentWithCourseAndGrade();

-- show all courses taken by a given student (student_id)
DELIMITER $$
CREATE PROCEDURE CoursesByStudentById(IN id INT)
BEGIN
SELECT s.name, GROUP_CONCAT(c.course_name SEPARATOR ', ') as courses_taken
from Students s
JOIN Enrollments e
ON e.student_id=s.student_id
JOIN Courses c
ON e.course_id=c.course_id
GROUP BY s.student_id;
END $$

DELIMITER ;
CALL CoursesByStudentById(1);

-- show average grade per course.
DELIMITER $$
CREATE PROCEDURE AverageGradePerCourse()
BEGIN
SELECT c.course_name, COUNT(*) as average_grade
from Students s
JOIN Enrollments e
ON e.student_id=s.student_id
JOIN Courses c
ON e.course_id=c.course_id
GROUP BY c.course_name;
END $$

DELIMITER ;
CALL AverageGradePerCourse();
