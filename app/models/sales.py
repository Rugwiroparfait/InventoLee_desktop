import sqlite3
from datetime import datetime

def add_sale(sale_data):
    """
    Add a new sale record to the database.
    
    :param sale_data: Dictionary containing sale details
    :return: ID of the newly added sale
    """
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    
    # First get the current item data to calculate profit if not provided
    cursor.execute("""
        SELECT price FROM clothing_items WHERE id = ?
    """, (sale_data['item_id'],))
    
    item_data = cursor.fetchone()
    if not item_data:
        conn.close()
        raise ValueError(f"Item with ID {sale_data['item_id']} not found")
    
    # Calculate cost price (from inventory)
    purchase_price = item_data[0]
    
    # Calculate total amount if not provided
    if 'total_amount' not in sale_data:
        sale_data['total_amount'] = sale_data['quantity'] * sale_data['unit_price']
    
    # Calculate profit if not explicitly set
    if 'profit' not in sale_data or sale_data['profit'] is None:
        # Profit = (sale price - purchase price) * quantity
        sale_data['profit'] = (sale_data['unit_price'] - purchase_price) * sale_data['quantity']
    
    cursor.execute("""
        INSERT INTO sales (
            date, item_id, quantity, unit_price, 
            total_amount, payment_method, profit, expense_notes
        ) VALUES (
            :date, :item_id, :quantity, :unit_price,
            :total_amount, :payment_method, :profit, :expense_notes
        )
    """, sale_data)
    
    sale_id = cursor.lastrowid
    
    # Update inventory quantity
    cursor.execute("""
        UPDATE clothing_items
        SET quantity = quantity - ?
        WHERE id = ?
    """, (sale_data['quantity'], sale_data['item_id']))
    
    conn.commit()
    conn.close()
    return sale_id

def get_all_sales(start_date=None, end_date=None):
    """
    Get all sales records, optionally filtered by date range.
    
    :param start_date: Optional start date for filtering (YYYY-MM-DD format)
    :param end_date: Optional end date for filtering (YYYY-MM-DD format)
    :return: List of sale records
    """
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    
    query = """
        SELECT s.id, s.date, i.name, s.quantity, s.unit_price, 
               s.total_amount, s.payment_method, s.profit, s.expense_notes
        FROM sales s
        JOIN clothing_items i ON s.item_id = i.id
    """
    
    params = []
    if start_date and end_date:
        query += " WHERE s.date BETWEEN ? AND ?"
        params = [start_date, end_date]
    elif start_date:
        query += " WHERE s.date >= ?"
        params = [start_date]
    elif end_date:
        query += " WHERE s.date <= ?"
        params = [end_date]
    
    query += " ORDER BY s.date DESC"
    
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
        
    sales = cursor.fetchall()
    conn.close()
    return sales

def get_summary(period_type="daily", start_date=None, end_date=None):
    """
    Get sales summary for specified period.
    
    :param period_type: Type of summary ("daily", "weekly", "monthly")
    :param start_date: Optional start date for filtering
    :param end_date: Optional end date for filtering
    :return: Dictionary with summary data
    """
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    
    # SQL date formatting based on period type
    if period_type == "daily":
        date_format = "%Y-%m-%d"
    elif period_type == "weekly":
        date_format = "%Y-%W"  # Year-Week number
    elif period_type == "monthly":
        date_format = "%Y-%m"
    else:
        date_format = "%Y-%m-%d"  # Default to daily
    
    query = f"""
        SELECT 
            strftime('{date_format}', date) as period,
            SUM(total_amount) as total_sales,
            SUM(CASE WHEN profit IS NULL THEN 0 ELSE profit END) as total_profit
        FROM sales
    """
    
    params = []
    if start_date and end_date:
        query += " WHERE date BETWEEN ? AND ?"
        params = [start_date, end_date]
    elif start_date:
        query += " WHERE date >= ?"
        params = [start_date]
    elif end_date:
        query += " WHERE date <= ?"
        params = [end_date]
    
    query += " GROUP BY period ORDER BY period"
    
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
        
    summaries = cursor.fetchall()
    conn.close()
    
    return summaries

def delete_last_sale():
    """Delete the most recently added sale and restore inventory"""
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    
    # Get the last sale
    cursor.execute("""
        SELECT id, item_id, quantity FROM sales
        ORDER BY id DESC LIMIT 1
    """)
    last_sale = cursor.fetchone()
    
    if last_sale:
        sale_id, item_id, quantity = last_sale
        
        # Restore inventory quantity
        cursor.execute("""
            UPDATE clothing_items
            SET quantity = quantity + ?
            WHERE id = ?
        """, (quantity, item_id))
        
        # Delete the sale
        cursor.execute("DELETE FROM sales WHERE id = ?", (sale_id,))
        
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

def delete_all_sales():
    """Delete all sales (CAUTION: This will not restore inventory)"""
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    
    # Delete all sales
    cursor.execute("DELETE FROM sales")
    
    conn.commit()
    conn.close()
    return True