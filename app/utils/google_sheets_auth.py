import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class GoogleSheetsAuth:
    """Handle authentication with Google Sheets API using service account credentials"""
    
    def __init__(self):
        """Initialize Google Sheets API authentication"""
        self.credentials = None
        self.client = None
        
        try:
            # Define the scope
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            
            # Path to credentials file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            credentials_path = os.path.join(current_dir, 'credentials.json')
            
            # Check if credentials file exists and is not empty
            if os.path.exists(credentials_path) and os.path.getsize(credentials_path) > 0:
                # Authenticate using the credentials file
                self.credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
                self.client = gspread.authorize(self.credentials)
        except Exception as e:
            print(f"Error initializing Google Sheets auth: {str(e)}")
            self.credentials = None
            self.client = None
    
    def is_authenticated(self):
        """Check if successfully authenticated with Google"""
        return self.client is not None
    
    def get_gspread_client(self):
        """Get the gspread client instance"""
        return self.client