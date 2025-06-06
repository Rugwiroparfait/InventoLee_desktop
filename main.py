import sys
import os
import json
from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow
from app.db import init_db

# Ensure utils directory exists
utils_dir = os.path.join('app', 'utils')
os.makedirs(utils_dir, exist_ok=True)

# Create placeholder credentials file if it doesn't exist
credentials_path = os.path.join(utils_dir, 'credentials.json')
if not os.path.exists(credentials_path):
    # Create an empty but valid JSON structure
    placeholder = {
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "",
        "private_key": "",
        "client_email": "",
        "client_id": "",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": ""
    }
    with open(credentials_path, 'w') as f:
        json.dump(placeholder, f, indent=4)

# Create config file if it doesn't exist
config_path = os.path.join(utils_dir, 'sheets_config.json')
if not os.path.exists(config_path):
    default_config = {
        'inventory_sheet_id': '',
        'inventory_sheet_name': 'Inventory',
        'sales_sheet_id': '',
        'sales_sheet_name': 'Sales',
    }
    with open(config_path, 'w') as f:
        json.dump(default_config, f, indent=4)

if __name__ == "__main__":
    init_db()  # Ensure database is initialized
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
