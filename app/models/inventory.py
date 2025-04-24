import sqlite3

def get_all_items():
    """
    Fetches all clothing items from the database.
    Returns a list of tuples, where each tuple represents a clothing item.
    Each tuple contains the following fields:
    - ID
    - Name
    - Category
    - Size
    - Color
    - Quantity
    - Price
    - Supplier
    - Expiry Date
    - Notes
    """

    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clothing_items")
    items = cursor.fetchall()
    conn.close()
    return items


def add_item_to_db(item):
    """
    adds a new clothing item to the database.
    The item parameter should be a tuple containing the following fields:
    - Name
    - Category
    - Size
    - Color
    - Quantity
    - Price
    - Supplier
    - Expiry Date
    - Notes
    The function inserts the item into the clothing_items table in the database.
    """
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO clothing_items (
            name, category, size, color, quantity, price,
            supplier, expiry_date, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, item)
    conn.commit()
    conn.close()
