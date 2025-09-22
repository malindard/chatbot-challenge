import sqlite3
from pathlib import Path
from typing import Optional, List, Dict

DB_PATH = Path("data/conversation_history.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Conversation History
def save_message(session_id: str, role: str, message: str):
    """Save conversation to history"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO conversation_history (session_id, role, message) VALUES (?, ?, ?)",
        (session_id, role, message)
    )
    conn.commit()
    conn.close()

def get_last_messages(session_id: str, limit: int = 3) -> List[Dict]:
    """Take the last message for certain session"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT role, message FROM conversation_history WHERE session_id=? ORDER BY timestamp DESC LIMIT ?",
        (session_id, limit * 2)  # user + bot = 2x
    )
    rows = cur.fetchall()
    conn.close()
    return [{"role": row["role"], "message": row["message"]} for row in reversed(rows)]

# Products
def get_product_by_name(name: str) -> Optional[Dict]:
    """Find product based on name(partial match)"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE name LIKE ? ORDER BY name LIMIT 1", (f"%{name}%",))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_products() -> List[Dict]:
    """Take all products"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, description, price FROM products ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Orders
def get_order_by_id(order_id: int) -> Optional[Dict]:
    """Find order based on ID"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE id=?", (order_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None