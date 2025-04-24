import sqlite3
from datetime import datetime

# Initialize Database
def init_db():
    """
    Initializes the database by creating the necessary tables if they do not already exist.

    This function connects to a SQLite database named "inventory.db" and creates two tables:
    1. `clothing_items`: Stores information about clothing items, including their name, category,
       size, color, quantity, price, supplier, expiry date, and additional notes.
    2. `transactions`: Tracks transactions related to clothing items, including the type of transaction
       ("in" for adding items or "out" for removing items), the quantity involved, the date of the
       transaction, and the reason for the transaction. This table has a foreign key relationship
       with the `clothing_items` table.

    After creating the tables, the function commits the changes and closes the database connection.
    """
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    # Create Clothing Items Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clothing_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        size TEXT,
        color TEXT,
        quantity INTEGER DEFAULT 0,
        price REAL,
        supplier TEXT,
        expiry_date TEXT,
        notes TEXT
    );
    """)

    # Create Transactions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        clothing_item_id INTEGER,
        transaction_type TEXT NOT NULL,  -- "in" or "out"
        quantity INTEGER,
        transaction_date TEXT,
        reason TEXT,
        FOREIGN KEY (clothing_item_id) REFERENCES clothing_items(id)
    );
    """)

    conn.commit()
    conn.close()

# Seed sample data
def seed_data():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    # Sample Inventory Items
    cursor.executemany("""
    INSERT INTO clothing_items (name, category, size, color, quantity, price, supplier, expiry_date, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        ("T-shirt", "Clothing", "M", "Red", 10, 15.99, "Supplier A", "2025-12-01", "Best seller"),
        ("Jeans", "Clothing", "L", "Blue", 5, 39.99, "Supplier B", "2026-05-01", "High quality denim"),
        ("Jacket", "Clothing", "S", "Black", 3, 59.99, "Supplier C", "2024-11-15", "Winter wear"),
    ])

    # Sample Transactions
    cursor.executemany("""
    INSERT INTO transactions (clothing_item_id, transaction_type, quantity, transaction_date, reason)
    VALUES (?, ?, ?, ?, ?)
    """, [
        (1, "in", 10, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Restocked"),
        (2, "out", 2, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Sold"),
        (3, "out", 1, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Returned by customer"),
    ])

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    seed_data()
    print("Database initialized and seeded with sample data!")
