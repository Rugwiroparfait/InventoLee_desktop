from PySide6.QtWidgets import QMainWindow, QLabel, QTabWidget
from app.ui.inventory_view import InventoryView
from app.ui.sales_view import SalesView  # Add this import

class MainWindow(QMainWindow):
    """
    MainWindow class for the InventoLee application.
    This class inherits from QMainWindow and serves as the main window for the application.
    It initializes the window title, geometry, and sets up the main tab widget.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("InventoLee - Clothing Inventory")
        self.setGeometry(100, 100, 1000, 700)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.inventory_tab = InventoryView()
        self.sales_tab = SalesView()  # Add this line
        
        self.tabs.addTab(self.inventory_tab, "🧥 Inventory")
        self.tabs.addTab(self.sales_tab, "💰 Sales Book")  # Add this line
