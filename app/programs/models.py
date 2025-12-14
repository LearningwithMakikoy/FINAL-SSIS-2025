from app.database import get_connection
from psycopg2.extras import RealDictCursor

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
            # Check if new code already exists (different program with same code)
            cur.execute("SELECT code FROM program WHERE code = %s AND code != %s;", 
                       (new_code, old_code))
            if cur.fetchone():
                raise ValueError(f"Program code '{new_code}' already exists")
            
            # Create the new program with new code
            cur.execute("""
                INSERT INTO program (code, name, college)
                VALUES (%s, %s, %s);
            """, (new_code, name, college))

            # Update any foreign key references (students that reference this program)
            cur.execute("""
                UPDATE student
                SET course = %s
                WHERE course = %s;
            """, (new_code, old_code))
            
            # Delete the old program
            cur.execute("DELETE FROM program WHERE code = %s;", (old_code,))
            
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


