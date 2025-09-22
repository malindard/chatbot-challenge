import os
import sqlite3
from pathlib import Path

DB_PATH = Path("data/conversation_history.db")
SCHEMA_PATH = Path("data/schema.sql")

def reset_database():
    """Reset database by deleting existing file"""
    try:
        # Delete database file if exists
        if DB_PATH.exists():
            os.remove(DB_PATH)
            print("=> Old database file deleted")
        
        print("=> Database reset complete")
        print("=> Run 'python data/init_db.py' to recreate")
        
    except Exception as e:
        print(f"Error resetting database: {e}")

def init_db():
    """Read schema.sql and create tables"""
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript(schema_sql)
    conn.commit()
    conn.close()
    print("=> Database initialized with schema.sql")

def seed():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Check if data already exists
    cur.execute("SELECT COUNT(*) FROM products")
    product_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM orders") 
    order_count = cur.fetchone()[0]

    if product_count > 0 and order_count > 0:
        print("=> Database already contains data, skipping seed...")
        conn.close()
        return

    # Seed products
    products_data = [
        ("Dress Summer", "Dress ringan berbahan katun premium, cocok untuk musim panas. Tersedia berbagai ukuran.", 299000, "Dress", 25),
        ("Jaket Denim", "Jaket denim unisex berkualitas tinggi, tahan lama dan stylish. Cocok untuk segala cuaca.", 459000, "Outerwear", 15),
        ("Kemeja Formal", "Kemeja formal pria berbahan cotton blend, perfect untuk acara resmi dan kantor.", 199000, "Shirt", 30),
        ("Celana Jeans", "Celana jeans wanita slim fit dengan stretch untuk kenyamanan maksimal.", 349000, "Pants", 20)
    ]

    for product in products_data:
        cur.execute("INSERT OR IGNORE INTO products (name, description, price, category, stock) VALUES (?, ?, ?, ?, ?)", product)

    # Seed orders
    orders_data = [
        (2001, "Olivia Carpenter", "Dikirim", "JNE", "2025-09-25", 299000),
        (2002, "Jenna Ortega", "Dikemas", "SiCepat", "2025-09-24", 459000),
        (2003, "Frank Ocean", "Menunggu Pembayaran", "-", "2025-09-23", 199000)
    ]

    for order in orders_data:
        cur.execute("INSERT OR IGNORE INTO orders (id, customer_name, status, shipping_provider, eta, total_amount) VALUES (?, ?, ?, ?, ?, ?)", order)

    conn.commit()
    
    # Verify data inserted
    cur.execute("SELECT COUNT(*) FROM products")
    product_final = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM orders")
    order_final = cur.fetchone()[0]
    
    conn.close()
    print(f"=> Database seeded successfully!")
    print(f"=> Products: {product_final} records")
    print(f"=> Orders: {order_final} records")

if __name__ == "__main__":
    reset_database()
    init_db()
    seed()