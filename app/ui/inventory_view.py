from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox
from app.ui.add_item_dialog import AddItemDialog
from app.models.inventory import delete_item_from_db , get_all_items , add_item_to_db, get_item_by_id, update_item_in_db  # Import the function to delete the item

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

            # Create Edit and Delete buttons
            edit_button = QPushButton("✏️ Edit")
            delete_button = QPushButton("🗑️ Delete")


            # Connect each button to its own item ID
            item_id = item[0]

            edit_button.clicked.connect(lambda _, id=item_id: self.edit_item(id))
            delete_button.clicked.connect(lambda _, id=item_id: self.delete_item(id))

            # Add buttons into a layouts
            button_layout = QHBoxLayout()
            button_layout.addWidget(edit_button)
            button_layout.addWidget(delete_button)

            # Create a widget to hold the buttons
            button_widget = QWidget()
            button_widget.setLayout(button_layout)

            # Add the button widget to the last column of the table
            self.table.setCellWidget(row, len(headers) - 1, button_widget)
    def edit_item(self, item_id):
        """
        Edit item
        """

        # Fetch the item details by ID
        item = get_item_by_id(item_id)
        if not item:
            QMessageBox.warning(self, "Edit Item", f"Item with ID: {item_id} not found.")
            return

        # Open the AddItemDialog pre-filled with the item's details
        dialog = AddItemDialog(self, item=item_id)
        if dialog.exec():
            # If the dialog is accepted, update the item in the database
            updated_item = dialog.get_item_data()
            update_item_in_db(item_id, updated_item)
            QMessageBox.information(self, "Edit Item", f"Item with ID: {item_id} updated successfully.")
            self.load_items()  # Reload the table to reflect the changes
    def delete_item(self, item_id):
        """
        Delete item
        """
        reply = QMessageBox.question(self, "Delete Item", f"Are you sure you want to delete item with ID: {item_id}?", QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Perform the deletion logic here
            
            delete_item_from_db(item_id)  # Delete the item from the database
            QMessageBox.information(self, "Delete Item", f"Item with ID: {item_id} deleted.")
            self.load_items()  # Reload the table to reflect the changes

    def show_add_dialog(self):
        """
        Dialog
        """
        dialog = AddItemDialog(self)
        if dialog.exec():
            self.load_items()



