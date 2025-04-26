import sqlite3
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox

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

def delete_item_from_db(item_id):
    """
    Deletes a clothing item from the database.
    The item_id parameter should be the ID of the item to be deleted.
    The function removes the item from the clothing_items table in the database.
    """
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clothing_items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()


def get_item_by_id(item_id):
    """
    Fetches an item from the database by its ID.
    :param item_id: The ID of the item to fetch.
    :return: A tuple representing the item, or None if not found.
    """
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clothing_items WHERE id=?", (item_id,))
    item = cursor.fetchone()
    conn.close()
    return item

def update_item_in_db(item_id, updated_item):
    """
    Updates an item in the database.
    :param item_id: The ID of the item to update.
    :param updated_item: A tuple containing the updated item data.
    """
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE clothing_items
        SET name=?, category=?, size=?, color=?, quantity=?, price=?, supplier=?, expiry_date=?, notes=?
        WHERE id=?
    """, (*updated_item, item_id))
    conn.commit()
    conn.close()
