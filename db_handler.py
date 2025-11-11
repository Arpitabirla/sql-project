# db_handler.py
import psycopg2
from psycopg2 import sql, OperationalError, DatabaseError

# --- UPDATE THESE to match your local Postgres setup ---
DB_CONFIG = {
    "host": "localhost",
    "database": "budget_manager",   # make sure this db exists
    "user": "postgres",
    "password": "989354",    # replace with your password
    "port": 5432
}
# ------------------------------------------------------

def connect():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except OperationalError as e:
        print("ERROR: could not connect to the database:", e)
        raise

def create_table():
    """Create transactions table if it doesn't exist. Call this once at startup."""
    conn = None
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                category VARCHAR(100) NOT NULL,
                description TEXT,
                amount NUMERIC(12,2) NOT NULL,
                type VARCHAR(10) NOT NULL CHECK (type IN ('income','expense'))
            );
        """)
        conn.commit()
        cur.close()
    except DatabaseError as e:
        print("DB error in create_table():", e)
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def add_transaction(date_str, category, amount, t_type, description=None):
    """
    Insert a transaction. IMPORTANT: pass amount as numeric (float or string numeric),
    and t_type should be exactly 'income' or 'expense'.
    """
    conn = None
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO transactions (date, category, description, amount, type)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """, (date_str, category, description, float(amount), t_type))
        inserted_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return inserted_id
    except Exception as e:
        print("Error in add_transaction():", e)
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def delete_transaction(transaction_id):
    conn = None
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM transactions WHERE id = %s RETURNING id;", (int(transaction_id),))
        res = cur.fetchone()
        conn.commit()
        cur.close()
        return res is not None
    except Exception as e:
        print("Error in delete_transaction():", e)
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def view_all():
    """Return rows as list of tuples: (id, date, category, description, amount, type)"""
    conn = None
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT id, date, category, description, amount, type FROM transactions ORDER BY id DESC;")
        rows = cur.fetchall()
        cur.close()
        return rows
    except Exception as e:
        print("Error in view_all():", e)
        raise
    finally:
        if conn:
            conn.close()

def get_summary():
    """Return (total_income, total_expense)"""
    conn = None
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN type='income' THEN amount END), 0) AS total_income,
                COALESCE(SUM(CASE WHEN type='expense' THEN amount END), 0) AS total_expense
            FROM transactions;
        """)
        row = cur.fetchone()
        cur.close()
        return float(row[0]), float(row[1])
    except Exception as e:
        print("Error in get_summary():", e)
        raise
    finally:
        if conn:
            conn.close()
