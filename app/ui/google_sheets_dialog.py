from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QLineEdit, QFormLayout, QTabWidget,
                             QMessageBox, QFrame, QFileDialog, QCheckBox, QGroupBox,
                             QWidget)  # Added QWidget here
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon
import os
from app.utils.google_sheets_sync import GoogleSheetsSync

class GoogleSheetsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Google Sheets Integration")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # Initialize the sheets sync utility
        self.sheets_sync = GoogleSheetsSync()
        
        # UI theme from parent
        if parent and hasattr(parent, 'colors'):
            self.colors = parent.colors
        else:
            # Default colors
            self.colors = {
                'primary': '#4A6FA5',
                'primary_light': '#6B8EB8',
                'background_light': '#FAF8F5',
                'text_primary': '#2D3142',
                'text_secondary': '#6B717E',
                'border': '#D5CEC8',
            }
        
        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Status header
        self.status_frame = QFrame()
        self.status_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['background_light']};
                border-radius: 6px;
                padding: 10px;
            }}
        """)
        status_layout = QVBoxLayout(self.status_frame)
        
        self.status_label = QLabel("Google Sheets Integration Status")
        self.status_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        status_layout.addWidget(self.status_label)
        
        self.status_details = QLabel()
        self.status_details.setWordWrap(True)
        status_layout.addWidget(self.status_details)
        
        layout.addWidget(self.status_frame)
        
        # Tabs for settings
        tabs = QTabWidget()
        
        # Inventory sheet settings
        inventory_tab = QWidget()
        inventory_layout = QFormLayout(inventory_tab)
        
        self.inventory_sheet_id = QLineEdit()
        self.inventory_sheet_name = QLineEdit("Inventory")
        
        inventory_layout.addRow("Spreadsheet ID:", self.inventory_sheet_id)
        inventory_layout.addRow("Worksheet Name:", self.inventory_sheet_name)
        
        inventory_info = QLabel(
            "Enter the Google Sheets spreadsheet ID where your inventory will be synced. "
            "You can find this in the URL of your spreadsheet: "
            "https://docs.google.com/spreadsheets/d/<spreadsheet_id>/edit"
        )
        inventory_info.setWordWrap(True)
        inventory_info.setStyleSheet(f"color: {self.colors['text_secondary']};")
        
        inventory_layout.addRow("", inventory_info)
        
        inventory_buttons = QHBoxLayout()
        self.sync_inventory_btn = QPushButton("Sync Inventory Now")
        self.sync_inventory_btn.clicked.connect(self.sync_inventory_data)
        inventory_buttons.addWidget(self.sync_inventory_btn)
        inventory_layout.addRow("", inventory_buttons)
        
        # Sales sheet settings
        sales_tab = QWidget()
        sales_layout = QFormLayout(sales_tab)
        
        self.sales_sheet_id = QLineEdit()
        self.sales_sheet_name = QLineEdit("Sales")
        
        sales_layout.addRow("Spreadsheet ID:", self.sales_sheet_id)
        sales_layout.addRow("Worksheet Name:", self.sales_sheet_name)
        
        sales_info = QLabel(
            "Enter the Google Sheets spreadsheet ID where your sales data will be synced. "
            "You can use the same spreadsheet as inventory with a different worksheet name."
        )
        sales_info.setWordWrap(True)
        sales_info.setStyleSheet(f"color: {self.colors['text_secondary']};")
        
        sales_layout.addRow("", sales_info)
        
        sales_buttons = QHBoxLayout()
        self.sync_sales_btn = QPushButton("Sync Sales Now")
        self.sync_sales_btn.clicked.connect(self.sync_sales_data)
        sales_buttons.addWidget(self.sync_sales_btn)
        sales_layout.addRow("", sales_buttons)
        
        # Add tabs
        tabs.addTab(inventory_tab, "Inventory Settings")
        tabs.addTab(sales_tab, "Sales Settings")
        layout.addWidget(tabs)
        
        # Credential file section
        creds_group = QGroupBox("Credentials")
        creds_layout = QVBoxLayout(creds_group)
        
        creds_info = QLabel(
            "To use Google Sheets integration, you need a service account credentials file. "
            "This file should be named 'credentials.json' and placed in the app/utils directory."
        )
        creds_info.setWordWrap(True)
        
        self.select_creds_btn = QPushButton("Select Credentials File")
        self.select_creds_btn.clicked.connect(self.select_credentials_file)
        
        creds_layout.addWidget(creds_info)
        creds_layout.addWidget(self.select_creds_btn)
        
        layout.addWidget(creds_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Settings")
        self.cancel_btn = QPushButton("Cancel")
        
        self.save_btn.clicked.connect(self.save_settings)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        # Load existing settings
        self.load_settings()
        
        # Update status
        self.update_status()
    
    def load_settings(self):
        """Load existing Google Sheets settings"""
        if self.sheets_sync.config:
            self.inventory_sheet_id.setText(self.sheets_sync.config.get('inventory_sheet_id', ''))
            self.inventory_sheet_name.setText(self.sheets_sync.config.get('inventory_sheet_name', 'Inventory'))
            self.sales_sheet_id.setText(self.sheets_sync.config.get('sales_sheet_id', ''))
            self.sales_sheet_name.setText(self.sheets_sync.config.get('sales_sheet_name', 'Sales'))
    
    def save_settings(self):
        """Save Google Sheets settings"""
        inventory_id = self.inventory_sheet_id.text().strip()
        inventory_name = self.inventory_sheet_name.text().strip() or "Inventory"
        
        sales_id = self.sales_sheet_id.text().strip()
        sales_name = self.sales_sheet_name.text().strip() or "Sales"
        
        self.sheets_sync.set_sheet_info('inventory', inventory_id, inventory_name)
        self.sheets_sync.set_sheet_info('sales', sales_id, sales_name)
        
        self.update_status()
        
        QMessageBox.information(self, "Settings Saved", 
                               "Google Sheets integration settings have been saved.")
        
        self.accept()
    
    def update_status(self):
        """Update the status display based on configuration"""
        if not self.sheets_sync.client:
            self.status_details.setText(
                "⚠️ Google Sheets API not configured. Missing or invalid credentials file."
            )
            self.status_details.setStyleSheet("color: #B95C50;")  # Error color
            self.sync_inventory_btn.setEnabled(False)
            self.sync_sales_btn.setEnabled(False)
            return
        
        if not self.sheets_sync.is_configured():
            self.status_details.setText(
                "⚙️ Connection to Google API available, but sheet settings incomplete. "
                "Please configure both inventory and sales spreadsheet IDs."
            )
            self.status_details.setStyleSheet("color: #D28A7A;")  # Warning color
            self.sync_inventory_btn.setEnabled(False)
            self.sync_sales_btn.setEnabled(False)
        else:
            self.status_details.setText(
                "✅ Google Sheets integration is fully configured and ready to use."
            )
            self.status_details.setStyleSheet("color: #508569;")  # Success color
            self.sync_inventory_btn.setEnabled(True)
            self.sync_sales_btn.setEnabled(True)
    
    def select_credentials_file(self):
        """Open file dialog to select and copy credentials file"""
        file_dialog = QFileDialog()
        creds_file, _ = file_dialog.getOpenFileName(
            self, "Select Google API Credentials File", "", 
            "JSON Files (*.json)"
        )
        
        if creds_file:
            try:
                # Destination path in the app/utils directory
                current_dir = os.path.dirname(os.path.abspath(__file__))
                utils_dir = os.path.join(os.path.dirname(current_dir), "utils")
                
                # Create utils directory if it doesn't exist
                if not os.path.exists(utils_dir):
                    os.makedirs(utils_dir)
                
                dest_path = os.path.join(utils_dir, "credentials.json")
                
                # Copy file (read source and write to destination)
                with open(creds_file, 'r') as src_file:
                    with open(dest_path, 'w') as dest_file:
                        dest_file.write(src_file.read())
                
                # Reinitialize sheets sync with new credentials
                self.sheets_sync = GoogleSheetsSync()
                self.update_status()
                
                QMessageBox.information(self, "Success", 
                                      "Credentials file has been successfully imported.")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                                   f"Failed to copy credentials file: {str(e)}")
    
    def sync_inventory_data(self):
        """Sync inventory data to Google Sheets"""
        success, message = self.sheets_sync.sync_inventory()
        
        if success:
            QMessageBox.information(self, "Sync Successful", message)
        else:
            QMessageBox.warning(self, "Sync Failed", message)
    
    def sync_sales_data(self):
        """Sync sales data to Google Sheets"""
        success, message = self.sheets_sync.sync_sales()
        
        if success:
            QMessageBox.information(self, "Sync Successful", message)
        else:
            QMessageBox.warning(self, "Sync Failed", message)