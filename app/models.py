# app/models.py
from flask_login import UserMixin
from .database import get_connection
from werkzeug.security import generate_password_hash

# ------------------------------
# User Model
# ------------------------------
class User(UserMixin):
    def __init__(self, id, username, email, password_hash):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash

    def __repr__(self):
        return f"<User {self.username}>"

    @staticmethod
    def get_by_id(user_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username, email, password_hash FROM users WHERE id = %s;", (user_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return User(*row)
        return None

    @staticmethod
    def get_by_username(username):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username, email, password_hash FROM users WHERE username = %s;", (username,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return User(*row)
        return None

    @staticmethod
    def create(username, email, password_hash):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id;",
            (username, email, password_hash)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return User.get_by_id(user_id)


# ------------------------------
# Student Model
# ------------------------------
class Student:
    def __init__(self, id, firstname, lastname, course, year, gender):
        self.id = id
        self.firstname = firstname
        self.lastname = lastname
        self.course = course
        self.year = year
        self.gender = gender

    @staticmethod
    def all():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT s.id, s.firstname, s.lastname, s.course, s.year, s.gender,
                   p.name AS program_name
            FROM student s
            LEFT JOIN program p ON s.course = p.code
            ORDER BY s.id;
        """)
        students = cur.fetchall()
        cur.close()
        conn.close()
        return students

    @staticmethod
    def get_by_id(student_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM student WHERE id=%s;", (student_id,))
        student = cur.fetchone()
        cur.close()
        conn.close()
        return student

    @staticmethod
    def create(id, firstname, lastname, course, year, gender):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO student (id, firstname, lastname, course, year, gender)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (id, firstname, lastname, course, year, gender))
        conn.commit()
        cur.close()
        conn.close()
        return Student.get_by_id(id)

    @staticmethod
    def update(id, firstname, lastname, course, year, gender):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE student
            SET firstname=%s, lastname=%s, course=%s, year=%s, gender=%s
            WHERE id=%s;
        """, (firstname, lastname, course, year, gender, id))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def delete(id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM student WHERE id=%s;", (id,))
        conn.commit()
        cur.close()
        conn.close()



# ------------------------------
# Program Model
# ------------------------------
class Program:
    def __init__(self, code, name, college):
        self.code = code
        self.name = name
        self.college = college

    @staticmethod
    def all():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT code, name, college FROM program ORDER BY name;")
        programs = cur.fetchall()
        cur.close()
        conn.close()
        return programs

    @staticmethod
    def get_by_code(code):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT code, name, college FROM program WHERE code=%s;", (code,))
        program = cur.fetchone()
        cur.close()
        conn.close()
        return program

    @staticmethod
    def create(code, name, college):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO program (code, name, college) VALUES (%s, %s, %s);",
                    (code, name, college))
        conn.commit()
        cur.close()
        conn.close()
        return Program.get_by_code(code)

    @staticmethod
    def update(code, name, college):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE program SET name=%s, college=%s WHERE code=%s;",
                    (name, college, code))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def delete(code):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM program WHERE code=%s;", (code,))
        conn.commit()
        cur.close()
        conn.close()


# ------------------------------
# College Model
# ------------------------------
class College:
    def __init__(self, code, name):
        self.code = code
        self.name = name

    @staticmethod
    def all():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT code, name FROM college ORDER BY name;")
        colleges = cur.fetchall()
        cur.close()
        conn.close()
        return colleges

    @staticmethod
    def get_by_code(code):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT code, name FROM college WHERE code=%s;", (code,))
        college = cur.fetchone()
        cur.close()
        conn.close()
        return college

    @staticmethod
    def create(code, name):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO college (code, name) VALUES (%s, %s);", (code, name))
        conn.commit()
        cur.close()
        conn.close()
        return College.get_by_code(code)

    @staticmethod
    def update(code, name):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE college SET name=%s WHERE code=%s;", (name, code))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def delete(code):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM college WHERE code=%s;", (code,))
        conn.commit()
        cur.close()
        conn.close()
