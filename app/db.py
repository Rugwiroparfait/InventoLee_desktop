import sqlite3
from datetime import datetime

# Initialize Database
def init_db():
    """
    Initializes the database by creating the necessary tables if they do not already exist.

    This function connects to a SQLite database named "inventory.db" and creates three tables:
    1. `clothing_items`: Stores information about clothing items, including their name, category,
       size, color, quantity, price, supplier, expiry date, and additional notes.
    2. `transactions`: Tracks transactions related to clothing items, including the type of transaction
       ("in" for adding items or "out" for removing items), the quantity involved, the date of the
       transaction, and the reason for the transaction. This table has a foreign key relationship
       with the `clothing_items` table.
    3. `sales`: Records sales transactions, including the date of sale, item sold, quantity, unit price,
       total amount, payment method, profit, and any expense notes. This table also has a foreign key
       relationship with the `clothing_items` table.

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
        description TEXT,  -- Changed from color to description
        quantity INTEGER DEFAULT 0,
        price REAL,
        supplier TEXT,
        entry_date TEXT,   -- Changed from expiry_date to entry_date
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

    # Create Sales Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        item_id INTEGER,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        total_amount REAL NOT NULL,
        payment_method TEXT NOT NULL,
        profit REAL,
        expense_notes TEXT,
        FOREIGN KEY (item_id) REFERENCES clothing_items(id)
    );
    """)

    conn.commit()
    conn.close()

# Seed sample data
def seed_data():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    # Sample Inventory Items with updated fields
    cursor.executemany("""
    INSERT INTO clothing_items (name, category, size, description, quantity, price, supplier, entry_date, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        ("T-shirt", "Clothing", "M", "Cotton round neck casual tee", 10, 15.99, "Supplier A", datetime.now().strftime('%Y-%m-%d'), "Best seller"),
        ("Jeans", "Clothing", "L", "Blue denim straight cut", 5, 39.99, "Supplier B", datetime.now().strftime('%Y-%m-%d'), "High quality denim"),
        ("Jacket", "Clothing", "S", "Black leather with zipper", 3, 59.99, "Supplier C", datetime.now().strftime('%Y-%m-%d'), "Winter wear"),
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

    # Sample Sales Data
    cursor.executemany("""
    INSERT INTO sales (date, item_id, quantity, unit_price, total_amount, payment_method, profit, expense_notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 1, 2, 15.99, 31.98, "Cash", 10.00, "None"),
        (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 2, 1, 39.99, 39.99, "Credit Card", 15.00, "None"),
        (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 3, 1, 59.99, 59.99, "Cash", 20.00, "Winter sale"),
    ])

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    seed_data()
    print("Database initialized and seeded with sample data!")
