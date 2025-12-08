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
    def get_filtered(search='', sort_by='id', sort_dir='asc', page=1, per_page=30):
        """
        Get filtered, sorted, and paginated students.
        Returns: (data, total_count)
        """
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build WHERE clause for search
        where_clauses = []
        params = []
        
        if search:
            search_term = f"%{search}%"
            where_clauses.append("""
                (s.firstname ILIKE %s OR 
                 s.lastname ILIKE %s OR 
                 s.id::text ILIKE %s OR
                 p.name ILIKE %s OR
                 s.course ILIKE %s)
            """)
            params.extend([search_term, search_term, search_term, search_term, search_term])
        
        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        # Validate and map sort column
        sort_column_map = {
            'id': 's.id',
            'id_number': 's.id',
            'first_name': 's.firstname',
            'last_name': 's.lastname',
            'program': 'p.name',
            'course': 's.course',
            'year': 's.year',
            'gender': 's.gender'
        }
        
        sort_column = sort_column_map.get(sort_by, 's.id')
        sort_direction = 'ASC' if sort_dir.lower() == 'asc' else 'DESC'
        
        # Get total count
        count_query = f"""
            SELECT COUNT(*) as total
            FROM student s
            LEFT JOIN program p ON s.course = p.code
            {where_sql}
        """
        cur.execute(count_query, params)
        total = cur.fetchone()['total']
        
        # Get paginated data
        offset = (page - 1) * per_page
        query = f"""
            SELECT s.id, s.firstname, s.lastname, s.course, s.year, s.gender, s.photo_url,
                   p.name AS program_name
            FROM student s
            LEFT JOIN program p ON s.course = p.code
            {where_sql}
            ORDER BY {sort_column} {sort_direction}
            LIMIT %s OFFSET %s
        """
        params.extend([per_page, offset])
        cur.execute(query, params)
        rows = cur.fetchall()
        
        cur.close()
        conn.close()
        
        # Transform to match frontend expectations
        transformed = [
            {
                'id': s['id'],
                'id_number': s['id'],
                'first_name': s['firstname'],
                'last_name': s['lastname'],
                'program': s['program_name'] or s['course'] or '',
                'course': s['course'],
                'year': s['year'],
                'gender': s['gender'],
                'photo_url': s.get('photo_url') or ''
            }
            for s in rows
        ]
        
        return transformed, total

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
    def get_filtered(search='', sort_by='name', sort_dir='asc', page=1, per_page=30):
        """
        Get filtered, sorted, and paginated programs.
        Returns: (data, total_count)
        """
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build WHERE clause for search
        where_clauses = []
        params = []
        
        if search:
            search_term = f"%{search}%"
            where_clauses.append("""
                (name ILIKE %s OR 
                 code ILIKE %s OR 
                 college ILIKE %s)
            """)
            params.extend([search_term, search_term, search_term])
        
        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        # Validate and map sort column
        sort_column_map = {
            'code': 'code',
            'name': 'name',
            'college': 'college'
        }
        
        sort_column = sort_column_map.get(sort_by, 'name')
        sort_direction = 'ASC' if sort_dir.lower() == 'asc' else 'DESC'
        
        # Get total count
        count_query = f"""
            SELECT COUNT(*) as total
            FROM program
            {where_sql}
        """
        cur.execute(count_query, params)
        total = cur.fetchone()['total']
        
        # Get paginated data
        offset = (page - 1) * per_page
        query = f"""
            SELECT code, name, college
            FROM program
            {where_sql}
            ORDER BY {sort_column} {sort_direction}
            LIMIT %s OFFSET %s
        """
        params.extend([per_page, offset])
        cur.execute(query, params)
        rows = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return rows, total

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
    def get_filtered(search='', sort_by='name', sort_dir='asc', page=1, per_page=30):
        """
        Get filtered, sorted, and paginated colleges.
        Returns: (data, total_count)
        """
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build WHERE clause for search
        where_clauses = []
        params = []
        
        if search:
            search_term = f"%{search}%"
            where_clauses.append("""
                (name ILIKE %s OR code ILIKE %s)
            """)
            params.extend([search_term, search_term])
        
        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        # Validate and map sort column
        sort_column_map = {
            'code': 'code',
            'name': 'name'
        }
        
        sort_column = sort_column_map.get(sort_by, 'name')
        sort_direction = 'ASC' if sort_dir.lower() == 'asc' else 'DESC'
        
        # Get total count
        count_query = f"""
            SELECT COUNT(*) as total
            FROM college
            {where_sql}
        """
        cur.execute(count_query, params)
        total = cur.fetchone()['total']
        
        # Get paginated data
        offset = (page - 1) * per_page
        query = f"""
            SELECT code, name
            FROM college
            {where_sql}
            ORDER BY {sort_column} {sort_direction}
            LIMIT %s OFFSET %s
        """
        params.extend([per_page, offset])
        cur.execute(query, params)
        rows = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return rows, total

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