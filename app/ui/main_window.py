from PySide6.QtWidgets import QMainWindow, QLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("InventoLee - Clothing Inventory")
        self.setGeometry(100, 100, 800, 600)

        label = QLabel("Welcome to InventoLee!", self)
        label.move(350, 280)
