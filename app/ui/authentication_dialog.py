from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QMessageBox, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import webbrowser
import threading
from app.utils.google_sheets_auth import GoogleSheetsAuth

class GoogleAuthDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Google Sheets Authentication")
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        
        # Initialize the authentication utility
        self.auth = GoogleSheetsAuth()
        
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
                padding: 20px;
            }}
        """)
        status_layout = QVBoxLayout(self.status_frame)
        
        self.status_label = QLabel("Google Sheets Authentication")
        self.status_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        status_layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.status_details = QLabel()
        self.status_details.setWordWrap(True)
        self.status_details.setFont(QFont("Segoe UI", 10))
        status_layout.addWidget(self.status_details, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.status_frame)
        
        # Info text
        info_text = QLabel(
            "InventoLee needs permission to access your Google Sheets. "
            "This allows you to sync inventory and sales data directly to your Google Sheets account."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet(f"color: {self.colors['text_secondary']};")
        layout.addWidget(info_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.auth_btn = QPushButton("Connect to Google Sheets")
        self.auth_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['primary']};
                color: white;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.colors['primary_light']};
            }}
        """)
        self.auth_btn.clicked.connect(self.start_authentication)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.auth_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        # Check existing authentication
        self.update_status()
    
    def update_status(self):
        """Update the status display based on authentication"""
        if self.auth.is_authenticated():
            self.status_details.setText(
                "✅ You are already connected to Google Sheets!\n\n"
                "You can proceed to configure which spreadsheets to use."
            )
            self.status_details.setStyleSheet("color: #508569;")  # Success color
            self.auth_btn.setText("Re-authenticate")
            self.setResult(QDialog.DialogCode.Accepted)
        else:
            self.status_details.setText(
                "❌ Not connected to Google Sheets.\n\n"
                "Click the button below to connect your Google account."
            )
            self.status_details.setStyleSheet("color: #B95C50;")  # Error color
            self.auth_btn.setText("Connect to Google Sheets")
            self.setResult(QDialog.DialogCode.Rejected)
    
    def start_authentication(self):
        """Start OAuth authentication flow"""
        try:
            # Generate the auth URL and get the server port
            auth_url, port = self.auth.get_auth_url()
            
            # Start the server in a separate thread
            self.auth.start_auth_server(port)
            
            # Update UI
            self.auth_btn.setEnabled(False)
            self.auth_btn.setText("Waiting for authentication...")
            self.status_details.setText("A browser window has been opened.\nPlease follow the instructions to authenticate.")
            self.status_details.setStyleSheet(f"color: {self.colors['text_secondary']};")
            
            # Open web browser
            webbrowser.open(auth_url)
            
            # Handle the callback in a separate thread
            def handle_auth():
                success, message = self.auth.handle_callback()
                # Update UI from main thread
                if success:
                    self.status_details.setText("✅ Authentication successful!")
                    self.status_details.setStyleSheet("color: #508569;")  # Success color
                    self.auth_btn.setText("Connected")
                    self.setResult(QDialog.DialogCode.Accepted)
                    self.accept()
                else:
                    self.status_details.setText(f"❌ {message}")
                    self.status_details.setStyleSheet("color: #B95C50;")  # Error color
                    self.auth_btn.setEnabled(True)
                    self.auth_btn.setText("Try Again")
            
            threading.Thread(target=handle_auth).start()
        
        except Exception as e:
            QMessageBox.critical(self, "Authentication Error", 
                               f"Failed to start authentication: {str(e)}")
            self.auth_btn.setEnabled(True)