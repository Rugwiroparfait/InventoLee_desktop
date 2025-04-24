import sys
from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow
from app.db import init_db

if __name__ == "__main__":
    init_db()  # Ensure database is initialized
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
