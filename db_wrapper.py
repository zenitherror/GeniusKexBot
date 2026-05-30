import os
import sqlite3
import logging
try:
    import psycopg2
    from psycopg2.extras import DictCursor
except ImportError:
    psycopg2 = None

logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "geniuskex.db")
IS_POSTGRES = DATABASE_URL.startswith("postgres")

def get_connection():
    if IS_POSTGRES and psycopg2:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        conn = sqlite3.connect(DATABASE_URL if not IS_POSTGRES else "geniuskex.db")
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    if IS_POSTGRES:
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            referral_code TEXT UNIQUE,
            referred_by BIGINT,
            referral_points INTEGER DEFAULT 0,
            daily_bonus_claimed_at TEXT
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            note_text TEXT
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS secret_vault (
            id SERIAL PRIMARY KEY,
            title TEXT,
            content TEXT,
            referral_unlock_count INTEGER DEFAULT 5
        )""")
        cursor.execute("SELECT COUNT(*) FROM secret_vault")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO secret_vault (title, content, referral_unlock_count) VALUES (%s, %s, %s)",
                      ("Traffic Hack #1", "Use viral loops: Give users a reason to share. Offer exclusive content behind referral walls.", 5))
            cursor.execute("INSERT INTO secret_vault (title, content, referral_unlock_count) VALUES (%s, %s, %s)",
                      ("Money Flow Secret", "Monetize attention: Every 1000 engaged users = $50-200/month via affiliate links, sponsored posts, or premium access.", 10))
    else:
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            referral_code TEXT UNIQUE,
            referred_by INTEGER,
            referral_points INTEGER DEFAULT 0,
            daily_bonus_claimed_at TEXT
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            note_text TEXT
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS secret_vault (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            referral_unlock_count INTEGER DEFAULT 5
        )""")
        cursor.execute("SELECT COUNT(*) FROM secret_vault")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO secret_vault (title, content, referral_unlock_count) VALUES (?, ?, ?)",
                      ("Traffic Hack #1", "Use viral loops: Give users a reason to share. Offer exclusive content behind referral walls.", 5))
            cursor.execute("INSERT INTO secret_vault (title, content, referral_unlock_count) VALUES (?, ?, ?)",
                      ("Money Flow Secret", "Monetize attention: Every 1000 engaged users = $50-200/month via affiliate links, sponsored posts, or premium access.", 10))
    
    conn.commit()
    conn.close()
    logger.info(f"Database initialized. Using {'PostgreSQL' if IS_POSTGRES else 'SQLite'}")

def execute_query(query, params=(), fetchone=False, fetchall=False, commit=False):
    conn = get_connection()
    if IS_POSTGRES:
        cursor = conn.cursor(cursor_factory=DictCursor)
        # Convert ? to %s for postgres
        query = query.replace("?", "%s")
    else:
        cursor = conn.cursor()
        
    try:
        cursor.execute(query, params)
        result = None
        if fetchone:
            result = cursor.fetchone()
            if result and IS_POSTGRES:
                result = dict(result)
        elif fetchall:
            result = cursor.fetchall()
            if result and IS_POSTGRES:
                result = [dict(r) for r in result]
        if commit:
            conn.commit()
        return result
    except Exception as e:
        logger.error(f"DB Error: {e}")
        if commit:
            conn.rollback()
        raise e
    finally:
        conn.close()
