from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QSpinBox, QDateEdit, QDoubleSpinBox
)
from PySide6.QtCore import QDate
from app.models.inventory import add_item_to_db

class AddItemDialog(QDialog):
    def __init__(self, parent=None, item=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Item" if item is None else "Edit Item")
        self.setMinimumWidth(400)
        self.item_id = None
        
        if isinstance(item, int):
            # If item is an ID, fetch the item data
            from app.models.inventory import get_item_by_id
            self.item_data = get_item_by_id(item)
            self.item_id = item
        else:
            self.item_data = item
        
        layout = QVBoxLayout()
        
        # Fields
        self.name = QLineEdit()
        self.category = QLineEdit()
        self.size = QLineEdit()
        self.description = QLineEdit()  # Changed from color to description
        self.quantity = QSpinBox()
        self.quantity.setMinimum(0)
        self.quantity.setMaximum(9999)
        self.price = QDoubleSpinBox()
        self.price.setMaximum(999999)
        self.price.setDecimals(2)
        self.supplier = QLineEdit()
        self.entry_date = QDateEdit()  # Changed from expiry to entry_date
        self.entry_date.setCalendarPopup(True)
        self.entry_date.setDate(QDate.currentDate())
        self.notes = QLineEdit()
        
        # Add fields with labels
        for label, widget in [
            ("Name", self.name),
            ("Category", self.category),
            ("Size", self.size),
            ("Description", self.description),  # Changed label from Color to Description
            ("Quantity", self.quantity),
            ("Price", self.price),
            ("Supplier", self.supplier),
            ("Entry Date", self.entry_date),  # Changed label from Expiry Date to Entry Date
            ("Notes", self.notes),
        ]:
            layout.addWidget(QLabel(label))
            layout.addWidget(widget)
        
        # Fill in the data if editing an existing item
        if self.item_data:
            self.prefill_data()
        
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
    
    def prefill_data(self):
        """Pre-fill form fields with existing item data when editing"""
        if not self.item_data:
            return
            
        self.name.setText(str(self.item_data[1]))
        self.category.setText(str(self.item_data[2]))
        self.size.setText(str(self.item_data[3]))
        self.description.setText(str(self.item_data[4]))  # Changed from color to description
        self.quantity.setValue(int(self.item_data[5]))
        self.price.setValue(float(self.item_data[6]))
        self.supplier.setText(str(self.item_data[7]))
        
        # Handle entry date
        try:
            entry_date_text = self.item_data[8]
            if entry_date_text:
                date = QDate.fromString(entry_date_text, "yyyy-MM-dd")
                if date.isValid():
                    self.entry_date.setDate(date)
        except:
            pass
            
        # Notes
        if len(self.item_data) > 9 and self.item_data[9]:
            self.notes.setText(str(self.item_data[9]))
    
    def save(self):
        """Save either updates an existing item or adds a new one"""
        data = self.get_item_data()
        
        if self.item_id:
            # Update existing item
            from app.models.inventory import update_item_in_db
            update_item_in_db(self.item_id, data)
        else:
            # Add new item
            from app.models.inventory import add_item_to_db
            add_item_to_db(data)
            
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
            "description": self.description.text(),  # Changed from color to description
            "quantity": self.quantity.value(),
            "price": self.price.value(),
            "supplier": self.supplier.text(),
            "entry_date": self.entry_date.date().toString("yyyy-MM-dd"),  # Changed from expiry_date to entry_date
            "notes": self.notes.text(),
        }