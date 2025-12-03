from flask_login import UserMixin
from .database import get_connection
from werkzeug.security import generate_password_hash
from psycopg2.extras import RealDictCursor



# USER MODEL

class User(UserMixin):
    def __init__(self, id, username, email, password_hash):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash

    @staticmethod
    def get_by_id(user_id):
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT id, username, email, password_hash
            FROM users
            WHERE id = %s;
        """, (user_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return User(row["id"], row["username"], row["email"], row["password_hash"])
        return None

    @staticmethod
    def get_by_username(username):
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT id, username, email, password_hash
            FROM users
            WHERE username = %s;
        """, (username,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return User(row["id"], row["username"], row["email"], row["password_hash"])
        return None
    
    @staticmethod
    def get_by_email(email):
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT id, username, email, password_hash
            FROM users
            WHERE email = %s;
            """, (email,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return User(row["id"], row["username"], row["email"], row["password_hash"])
        return None
        
    
    @staticmethod
    def create(username, email, password_hash):
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id;
        """, (username, email, password_hash))
        user_id = cur.fetchone()["id"]
        conn.commit()
        cur.close()
        conn.close()
        return User.get_by_id(user_id)



# STUDENT MODEL

class Student:

    @staticmethod
    def all():
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT s.id, s.firstname, s.lastname, s.course, s.year, s.gender, s.photo_url,
                   p.name AS program_name
            FROM student s
            LEFT JOIN program p ON s.course = p.code
            ORDER BY s.id;
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    @staticmethod
    def get_by_id(student_id):
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM student WHERE id = %s;", (student_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row

    @staticmethod
    def create(id, firstname, lastname, course, year, gender, photo_url=None):
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            INSERT INTO student (id, firstname, lastname, course, year, gender, photo_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (id, firstname, lastname, course, year, gender, photo_url))
        conn.commit()
        cur.close()
        conn.close()
        return Student.get_by_id(id)

    @staticmethod
    def update(old_id, new_id, firstname, lastname, course, year, gender, photo_url=None):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE student
            SET id=%s, firstname=%s, lastname=%s, course=%s, year=%s, gender=%s, photo_url=%s
            WHERE id=%s;
        """, (new_id, firstname, lastname, course, year, gender, photo_url, old_id))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def delete(id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM student WHERE id = %s;", (id,))
        conn.commit()
        cur.close()
        conn.close()


# PROGRAM MODEL
class Program:

    @staticmethod
    def all():
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT code, name, college
            FROM program
            ORDER BY name;
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    @staticmethod
    def get_by_code(code):
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT code, name, college
            FROM program
            WHERE code=%s;
        """, (code,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row

    @staticmethod
    def create(code, name, college):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO program (code, name, college)
            VALUES (%s, %s, %s);
        """, (code, name, college))
        conn.commit()
        cur.close()
        conn.close()
        return Program.get_by_code(code)

    @staticmethod
    def update(code, name, college):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE program
            SET name=%s, college=%s
            WHERE code=%s;
        """, (name, college, code))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def update_code(old_code, new_code, name, college):
        """Update program code (primary key) - requires delete and recreate"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            # First update any foreign key references (students that reference this program)
            cur.execute("""
                UPDATE student
                SET course = %s
                WHERE course = %s;
            """, (new_code, old_code))
            
            # Delete the old program
            cur.execute("DELETE FROM program WHERE code = %s;", (old_code,))
            
            # Create the new program with new code
            cur.execute("""
                INSERT INTO program (code, name, college)
                VALUES (%s, %s, %s);
            """, (new_code, name, college))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def delete(code):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM program WHERE code = %s;", (code,))
        conn.commit()
        cur.close()
        conn.close()



# COLLEGE MODEL
class College:

    @staticmethod
    def all():
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT code, name
            FROM college
            ORDER BY name;
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    @staticmethod
    def get_by_code(code):
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT code, name
            FROM college
            WHERE code=%s;
        """, (code,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row

    @staticmethod
    def create(code, name):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO college (code, name)
            VALUES (%s, %s);
        """, (code, name))
        conn.commit()
        cur.close()
        conn.close()
        return College.get_by_code(code)

    @staticmethod
    def update(code, name):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE college
            SET name=%s
            WHERE code=%s;
        """, (name, code))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def update_code(old_code, new_code, name):
        """Update college code (primary key) - requires delete and recreate"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            # First update any foreign key references (programs that reference this college)
            cur.execute("""
                UPDATE program
                SET college = %s
                WHERE college = %s;
            """, (new_code, old_code))
            
            # Delete the old college
            cur.execute("DELETE FROM college WHERE code = %s;", (old_code,))
            
            # Create the new college with new code
            cur.execute("""
                INSERT INTO college (code, name)
                VALUES (%s, %s);
            """, (new_code, name))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def delete(code):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM college WHERE code = %s;", (code,))
        conn.commit()
        cur.close()
        conn.close()
