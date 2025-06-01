import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sqlite3
from datetime import datetime

class GoogleSheetsSync:
    def __init__(self):
        """Initialize Google Sheets API client with OAuth credentials"""
        try:
            # Define the scope
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            
            # Path to credentials file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            credentials_path = os.path.join(current_dir, 'credentials.json')
            
            # Authenticate using the credentials file
            credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
            self.client = gspread.authorize(credentials)
            
            # Configuration file path
            config_path = os.path.join(current_dir, 'sheets_config.json')
            
            # Load configuration
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
            else:
                # Default configuration
                self.config = {
                    'inventory_sheet_id': '',
                    'inventory_sheet_name': 'Inventory',
                    'sales_sheet_id': '',
                    'sales_sheet_name': 'Sales',
                }
                # Save default configuration
                with open(config_path, 'w') as f:
                    json.dump(self.config, f, indent=4)
        
        except Exception as e:
            print(f"Error initializing Google Sheets sync: {str(e)}")
            self.client = None
            self.config = None
    
    def is_configured(self):
        """Check if the Google Sheets integration is properly configured"""
        return (self.client is not None and
                self.config is not None and
                self.config.get('inventory_sheet_id') and
                self.config.get('sales_sheet_id'))
    
    def set_sheet_info(self, sheet_type, sheet_id, sheet_name):
        """
        Update sheet configuration
        
        :param sheet_type: 'inventory' or 'sales'
        :param sheet_id: Google Sheets spreadsheet ID
        :param sheet_name: Worksheet name within the spreadsheet
        """
        if not self.config:
            return False
        
        if sheet_type == 'inventory':
            self.config['inventory_sheet_id'] = sheet_id
            self.config['inventory_sheet_name'] = sheet_name
        elif sheet_type == 'sales':
            self.config['sales_sheet_id'] = sheet_id
            self.config['sales_sheet_name'] = sheet_name
        
        # Save updated configuration
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, 'sheets_config.json')
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
        
        return True
    
    def sync_inventory(self):
        """Sync inventory data to Google Sheets"""
        if not self.is_configured():
            return False, "Google Sheets integration not configured"
        
        try:
            # Connect to the spreadsheet
            spreadsheet = self.client.open_by_key(self.config['inventory_sheet_id'])
            
            # Get the worksheet, or create it if it doesn't exist
            try:
                worksheet = spreadsheet.worksheet(self.config['inventory_sheet_name'])
                # Clear existing data (keeping header)
                if worksheet.row_count > 1:
                    worksheet.delete_rows(2, worksheet.row_count)
            except gspread.exceptions.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(
                    title=self.config['inventory_sheet_name'], 
                    rows=100, cols=10
                )
            
            # Set headers
            headers = ['ID', 'Name', 'Category', 'Size', 'Description', 
                      'Quantity', 'Price', 'Supplier', 'Entry Date', 'Notes']
            worksheet.update('A1:J1', [headers])
            
            # Format headers
            worksheet.format('A1:J1', {
                'backgroundColor': {'red': 0.2, 'green': 0.3, 'blue': 0.5},
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}}
            })
            
            # Get inventory data
            conn = sqlite3.connect('inventory.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM clothing_items')
            items = cursor.fetchall()
            conn.close()
            
            # Update worksheet with inventory data
            if items:
                worksheet.append_rows(items)
            
            # Auto-resize columns for better readability
            worksheet.columns_auto_resize(0, len(headers))
            
            return True, f"Successfully synced {len(items)} inventory items to Google Sheets"
            
        except Exception as e:
            return False, f"Error syncing inventory: {str(e)}"
    
    def sync_sales(self, start_date=None, end_date=None):
        """
        Sync sales data to Google Sheets
        
        :param start_date: Optional start date filter (YYYY-MM-DD)
        :param end_date: Optional end date filter (YYYY-MM-DD)
        """
        if not self.is_configured():
            return False, "Google Sheets integration not configured"
        
        try:
            # Connect to the spreadsheet
            spreadsheet = self.client.open_by_key(self.config['sales_sheet_id'])
            
            # Get the worksheet, or create it if it doesn't exist
            try:
                worksheet = spreadsheet.worksheet(self.config['sales_sheet_name'])
                # Clear existing data (keeping header)
                if worksheet.row_count > 1:
                    worksheet.delete_rows(2, worksheet.row_count)
            except gspread.exceptions.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(
                    title=self.config['sales_sheet_name'], 
                    rows=100, cols=9
                )
            
            # Set headers
            headers = ['ID', 'Date', 'Item', 'Quantity', 'Unit Price', 
                      'Total Amount', 'Payment Method', 'Profit', 'Notes']
            worksheet.update('A1:I1', [headers])
            
            # Format headers
            worksheet.format('A1:I1', {
                'backgroundColor': {'red': 0.2, 'green': 0.3, 'blue': 0.5},
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}}
            })
            
            # Get sales data
            conn = sqlite3.connect('inventory.db')
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
            
            # Update worksheet with sales data
            if sales:
                worksheet.append_rows(sales)
            
            # Auto-resize columns for better readability
            worksheet.columns_auto_resize(0, len(headers))
            
            # Format currency columns
            if len(sales) > 0:
                # Format unit price, total amount and profit as currency
                worksheet.format(f'E2:E{len(sales)+1}', {'numberFormat': {'type': 'CURRENCY'}})
                worksheet.format(f'F2:F{len(sales)+1}', {'numberFormat': {'type': 'CURRENCY'}})
                worksheet.format(f'H2:H{len(sales)+1}', {'numberFormat': {'type': 'CURRENCY'}})
                
                # Format date column
                worksheet.format(f'B2:B{len(sales)+1}', {'numberFormat': {'type': 'DATE', 'pattern': 'yyyy-mm-dd'}})
            
            return True, f"Successfully synced {len(sales)} sales records to Google Sheets"
            
        except Exception as e:
            return False, f"Error syncing sales: {str(e)}"