from flask_login import UserMixin
from app.database import get_connection
from psycopg2.extras import RealDictCursor

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

