import sqlite3

def get_all_items():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clothing_items")
    items = cursor.fetchall()
    conn.close()
    return items
