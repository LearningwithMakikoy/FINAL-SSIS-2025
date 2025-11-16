CREATE TABLE college (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE program (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    college VARCHAR(10),
    CONSTRAINT fk_program_college
        FOREIGN KEY (college)
        REFERENCES college(code)
        ON DELETE SET NULL         
);

CREATE TABLE student (
    id VARCHAR(10) PRIMARY KEY,           
    firstname VARCHAR(100) NOT NULL,
    lastname VARCHAR(100) NOT NULL,
    course VARCHAR(10),                  
    year INTEGER NOT NULL,
    gender VARCHAR(10) NOT NULL,
    CONSTRAINT fk_student_program
        FOREIGN KEY (course)
        REFERENCES program(code)
        ON DELETE SET NULL                
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);
