USE schooldb;

CREATE TABLE Teachers(
	teacher_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50),
    subject_id INT
    );

CREATE TABLE Subjects(
	subject_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_name VARCHAR(50)
);

INSERT INTO Subjects (subject_name) VALUES
('Mathematics'),   -- id = 1
('Science'),       -- id = 2
('English'),       -- id = 3
('History'),       -- id = 4
('Geography');     -- id = 5 (no teacher yet)

INSERT INTO Teachers (name, subject_id) VALUES
('Rahul Sir', 1),   -- Mathematics
('Priya Madam', 2), -- Science
('Arjun Sir', NULL),-- No subject assigned
('Neha Madam', 3);  -- English

SELECT t.name, s.subject_name
FROM Teachers t
INNER JOIN Subjects s
ON t.subject_id=s.subject_id;

SELECT t.name, s.subject_name
FROM Teachers t
LEFT JOIN Subjects s
ON t.subject_id=s.subject_id;

SELECT t.name, s.subject_name
FROM Teachers t
RIGHT JOIN Subjects s
ON t.subject_id=s.subject_id;


SELECT t.name, s.subject_name
FROM Teachers t
LEFT JOIN Subjects s
ON t.subject_id=s.subject_id

UNION

SELECT t.name, s.subject_name
FROM Teachers t
RIGHT JOIN Subjects s
ON t.subject_id=s.subject_id;