from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QSpinBox, QDateEdit, QDoubleSpinBox
)
from PySide6.QtCore import QDate
from app.models.inventory import add_item_to_db

class AddItemDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Item")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Fields
        self.name = QLineEdit()
        self.category = QLineEdit()
        self.size = QLineEdit()
        self.color = QLineEdit()
        self.quantity = QSpinBox()
        self.price = QDoubleSpinBox()
        self.price.setMaximum(999999)
        self.supplier = QLineEdit()
        self.expiry = QDateEdit()
        self.expiry.setCalendarPopup(True)
        self.expiry.setDate(QDate.currentDate())
        self.notes = QLineEdit()

        for label, widget in [
            ("Name", self.name),
            ("Category", self.category),
            ("Size", self.size),
            ("Color", self.color),
            ("Quantity", self.quantity),
            ("Price", self.price),
            ("Supplier", self.supplier),
            ("Expiry Date", self.expiry),
            ("Notes", self.notes),
        ]:
            layout.addWidget(QLabel(label))
            layout.addWidget(widget)

        # Buttons
        btns = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        btns.addWidget(self.save_btn)
        btns.addWidget(self.cancel_btn)
        layout.addLayout(btns)

        self.setLayout(layout)

        self.save_btn.clicked.connect(self.save)
        self.cancel_btn.clicked.connect(self.reject)

    def save(self):
        item = (
            self.name.text(),
            self.category.text(),
            self.size.text(),
            self.color.text(),
            self.quantity.value(),
            self.price.value(),
            self.supplier.text(),
            self.expiry.date().toString("yyyy-MM-dd"),
            self.notes.text(),
        )
        add_item_to_db(item)
        self.accept()
    
    def get_item_data(self):
        """
        Collect and return the item data from the dialog fields.
        Returns a dictionary with the item data.
        """
        return {
            "name": self.name.text(),
            "category": self.category.text(),
            "size": self.size.text(),
            "color": self.color.text(),
            "quantity": self.quantity.value(),
            "price": self.price.value(),
            "supplier": self.supplier.text(),
            "expiry_date": self.expiry.date().toString("yyyy-MM-dd"),
            "notes": self.notes.text(),
        }