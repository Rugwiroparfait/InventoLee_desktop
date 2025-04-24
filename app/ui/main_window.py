from PySide6.QtWidgets import QMainWindow, QLabel, QTabWidget
from app.ui.inventory_view import InventoryView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("InventoLee - Clothing Inventory")
        self.setGeometry(100, 100, 800, 600)

        label = QLabel("Welcome to InventoLee!", self)
        label.move(350, 280)

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
        self.tabs.addTab(self.inventory_tab, "🧥 Inventory")