from flask_login import UserMixin
from app.database import get_connection
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

