from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox

class GoogleAuthDialog(QDialog):
    """
    Placeholder for the OAuth authentication dialog.
    Currently using service account authentication instead.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Google Authentication")
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        label = QLabel("Using service account authentication.\nOAuth login not implemented in this version.")
        layout.addWidget(label)
        
        button = QPushButton("OK")
        button.clicked.connect(self.accept)
        layout.addWidget(button)
    
    def exec(self):
        QMessageBox.information(self, "Authentication Info", 
                               "OAuth authentication is not used in this version.\n"
                               "Please use the service account credentials file instead.")
        return False