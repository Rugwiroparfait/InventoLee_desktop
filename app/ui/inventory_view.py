from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout
from app.ui.add_item_dialog import AddItemDialog

"""
Module: inventory_view
----------------------

This module defines the `InventoryView` class, which provides a graphical user interface (GUI) for displaying and managing inventory items in a table format.

Classes:
--------
- InventoryView(QWidget): A QWidget subclass that displays a table of inventory items and provides an "Add Item" button for user interaction.

Methods:
--------
- __init__(): Initializes the InventoryView widget, sets up the layout, and loads inventory items into the table.
- load_items(): Fetches inventory data using the `get_all_items` function, populates the table with the data, and sets up column headers.

Attributes:
-----------
- layout (QVBoxLayout): The main vertical layout of the widget.
- add_button (QPushButton): A button for adding new inventory items.
- table (QTableWidget): A table widget for displaying inventory items.

Dependencies:
-------------
- PySide6.QtWidgets: Provides the GUI components such as QWidget, QVBoxLayout, QPushButton, QTableWidget, etc.
- app.models.inventory.get_all_items: A function that retrieves all inventory items from the data source.

Usage:
------
This class is intended to be used as part of a PySide6-based desktop application for managing inventory. It provides a user-friendly interface for viewing and interacting with inventory data.
"""
from app.models.inventory import get_all_items

class InventoryView(QWidget):
    def __init__(self):
        """
        Initializes the InventoryView widget.
        Sets up the layout, adds an "Add Item" button, and loads inventory items into the table.
        """
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Header / Actions
        btn_layout = QHBoxLayout()
        self.add_button = QPushButton("➕ Add Item")
        btn_layout.addWidget(self.add_button)
        btn_layout.addStretch()
        self.layout.addLayout(btn_layout)

        # connect the button to the method
        self.add_button.clicked.connect(self.show_add_dialog)

        # Inventory Table
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.load_items()

    def load_items(self):
        """
        Load inventory items into the table widget.
        This method retrieves all items from the data source using the `get_all_items` function,
        populates the table with the retrieved data, and sets up the column headers.
        """
        # Fetch all items from the data source
        # and populate the table
        items = get_all_items()
        headers = ["ID", "Name", "Category", "Size", "Color", "Qty", "Price", "Supplier", "Expiry", "Notes"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(items))

        for row, item in enumerate(items):
            # Populate each row with item data
            for col, value in enumerate(item):
                # Convert non-string values to string for display
                self.table.setItem(row, col, QTableWidgetItem(str(value)))

    def show_add_dialog(self):
        """
        Dialog
        """
        dialog = AddItemDialog(self)
        if dialog.exec():
            self.load_items()
