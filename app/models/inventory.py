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
    - Description (changed from Color)
    - Quantity
    - Price
    - Supplier
    - Entry Date (changed from Expiry Date)
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
    Adds a new clothing item to the database.
    The item parameter should be a dictionary containing the item data.
    """
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    
    # Check if a similar item already exists
    cursor.execute("""
        SELECT id FROM clothing_items 
        WHERE name=? AND description=? AND size=?
    """, (item['name'], item['description'], item['size']))
    
    existing = cursor.fetchone()
    
    if existing:
        # Item exists, maybe update quantity instead?
        cursor.execute("""
            UPDATE clothing_items
            SET quantity = quantity + ?
            WHERE id = ?
        """, (item['quantity'], existing[0]))
    else:
        # Insert new item
        cursor.execute("""
            INSERT INTO clothing_items (
                name, category, size, description, quantity, price,
                supplier, entry_date, notes
            ) VALUES (
                :name, :category, :size, :description, :quantity, :price,
                :supplier, :entry_date, :notes
            )
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
    :param updated_item: A dictionary containing the updated item data.
    """
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE clothing_items
        SET name=:name, 
            category=:category, 
            size=:size, 
            description=:description, 
            quantity=:quantity, 
            price=:price, 
            supplier=:supplier, 
            entry_date=:entry_date, 
            notes=:notes
        WHERE id=:id
    """, {**updated_item, 'id': item_id})
    conn.commit()
    conn.close()
