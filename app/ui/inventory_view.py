from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QTableWidget, 
                              QTableWidgetItem, QHBoxLayout, QMessageBox, QLabel,
                              QHeaderView, QFrame, QSplitter, QSpacerItem, QSizePolicy)
from PySide6.QtGui import QColor, QBrush, QFont, QIcon, QPalette, QLinearGradient, QPixmap
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from app.ui.add_item_dialog import AddItemDialog
from app.models.inventory import (delete_item_from_db, get_all_items, add_item_to_db, 
                                get_item_by_id, update_item_in_db)

"""
Module: inventory_view
----------------------

This module defines the `InventoryView` class, which provides a graphical user interface (GUI) 
for displaying and managing inventory items in a colorful, professional table format.

Classes:
--------
- InventoryView(QWidget): A QWidget subclass that displays a table of inventory items with
  elegant styling and animated buttons for user interaction.

Methods:
--------
- __init__(): Initializes the InventoryView widget with professional styling.
- load_items(): Populates the table with inventory data and applies styling.
- edit_item(): Opens dialog to edit an existing inventory item.
- delete_item(): Prompts for confirmation and deletes an item.
- show_add_dialog(): Opens dialog to add a new inventory item.
- setup_ui_theme(): Sets up the color scheme and styling for the interface.

Dependencies:
-------------
- PySide6.QtWidgets: GUI components
- PySide6.QtGui: Styling and visual elements
- PySide6.QtCore: Core functionality for animations and properties
- app.models.inventory: Functions for database operations
"""

class StyledButton(QPushButton):
    """
    Custom styled button with hover effects and optional icon
    """
    def __init__(self, text, icon_name=None, color_scheme=None):
        super().__init__(text)
        
        # Default color scheme
        self.base_color = "#6200EA" if not color_scheme else color_scheme["base"]
        self.hover_color = "#9D46FF" if not color_scheme else color_scheme["hover"]
        self.text_color = "#FFFFFF" if not color_scheme else color_scheme["text"]
        
        # Apply basic styling
        self.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(36)
        
        # Style sheet
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.base_color};
                color: {self.text_color};
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }}
            
            QPushButton:hover {{
                background-color: {self.hover_color};
            }}
            
            QPushButton:pressed {{
                background-color: {self.base_color};
            }}
        """)
        
        # Set icon if provided
        if icon_name:
            self.setIcon(QIcon(f":/icons/{icon_name}.png"))
            self.setIconSize(QSize(16, 16))


class InventoryView(QWidget):
    def __init__(self):
        """
        Initializes the InventoryView widget with professional styling.
        """
        super().__init__()
        
        # Set color palette and theme
        self.setup_ui_theme()
        
        # Main layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        self.setLayout(self.layout)
        
        # Header section with title and description
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout(header_frame)
        
        # Title and subtitle
        title_label = QLabel("Inventory Management")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {self.colors['primary']};")
        
        subtitle_label = QLabel("Manage your items with ease and efficiency")
        subtitle_label.setFont(QFont("Segoe UI", 10))
        subtitle_label.setStyleSheet(f"color: {self.colors['text_secondary']};")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        self.layout.addWidget(header_frame)
        
        # Actions toolbar
        toolbar_frame = QFrame()
        toolbar_frame.setObjectName("toolbarFrame")
        toolbar_frame.setStyleSheet(f"""
            #toolbarFrame {{
                background-color: {self.colors['background_light']};
                border-radius: 8px;
                padding: 8px;
            }}
        """)
        
        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add item button with custom styling
        self.add_button = StyledButton("➕ Add Item", color_scheme={
            "base": self.colors['primary'],
            "hover": self.colors['primary_light'],
            "text": "#FFFFFF"
        })
        self.add_button.clicked.connect(self.show_add_dialog)
        
        # Search field placeholder - could be expanded in future
        toolbar_layout.addWidget(self.add_button)
        toolbar_layout.addStretch()
        
        self.layout.addWidget(toolbar_frame)
        
        # Table container with shadow effect
        table_container = QFrame()
        table_container.setObjectName("tableContainer")
        table_container.setStyleSheet(f"""
            #tableContainer {{
                background-color: {self.colors['background_light']};
                border-radius: 8px;p
                padding: 1px;
            }}
        """)
        
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(5, 5, 5, 5)  # Increased from 2,2,2,2
        
        # Inventory Table
        self.table = QTableWidget()
        self.table.setFont(QFont("Segoe UI", 9))
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        
        # Table styling
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {self.colors['background_light']};
                alternate-background-color: {self.colors['background_alt']};
                border: none;
                border-radius: 8px;
                gridline-color: {self.colors['border']};
            }}
            
            QTableWidget::item {{
                padding: 12px 8px;  /* Increase padding for more space */
                border-bottom: 1px solid {self.colors['border']};
            }}
            
            QTableWidget::item:selected {{
                background-color: {self.colors['selection']};
                color: {self.colors['text_primary']};
            }}
            
            QHeaderView::section {{
                background-color: {self.colors['header']};
                color: {self.colors['text_primary']};
                font-weight: bold;
                padding: 12px;  /* Increase padding for header */
                border: none;
                border-bottom: 2px solid {self.colors['primary']};
                border-right: 1px solid {self.colors['border']};
            }}
        """)
        
        table_layout.addWidget(self.table)
        self.layout.addWidget(table_container)
        
        # Status bar
        status_bar = QFrame()
        status_bar.setObjectName("statusBar")
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(5, 0, 5, 0)
        
        status_label = QLabel("Ready")
        status_label.setStyleSheet(f"color: {self.colors['text_secondary']};")
        status_layout.addWidget(status_label)
        status_layout.addStretch()
        
        self.layout.addWidget(status_bar)
        
        # Load items into the table
        self.load_items()

    def setup_ui_theme(self):
        """
        Sets up an elegant color scheme and styling for the interface
        """
        # Elegant color palette
        self.colors = {
            'primary': '#4A6FA5',           # Slate Blue
            'primary_light': '#6B8EB8',     # Lighter Slate Blue
            'primary_dark': '#304C74',      # Darker Slate Blue
            'secondary': '#3D7068',         # Teal
            'secondary_light': '#5E9088',   # Lighter Teal
            'secondary_dark': '#28504A',    # Darker Teal
            'accent': '#D28A7A',            # Terracotta
            'background': '#F4F1ED',        # Eggshell
            'background_light': '#FAF8F5',  # Ivory (no pure white)
            'background_alt': '#ECE8E3',    # Light Taupe
            'text_primary': '#2D3142',      # Dark Charcoal Blue
            'text_secondary': '#6B717E',    # Medium Slate Gray
            'border': '#D5CEC8',            # Light Taupe
            'header': '#EAE6E1',            # Warmer Light Taupe
            'selection': '#E3E9F2',         # Very Light Blue Gray
            'delete': '#B95C50',            # Warm Red
            'delete_hover': '#CF7A70',      # Light Warm Red
            'edit': '#508569',              # Forest Green
            'edit_hover': '#6CA388',        # Light Forest Green
            'profit': '#508569',            # Forest Green
            'loss': '#B95C50',              # Warm Red
        }
        
        # Set widget background
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors['background']};
                color: {self.colors['text_primary']};
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }}
        """)

    def load_items(self):
        """
        Load inventory items into the table widget with professional styling.
        """
        # Fetch all items from the data source
        items = get_all_items()
        headers = ["ID", "Name", "Category", "Size", "Color", "Qty", "Price", "Supplier", "Expiry", "Actions"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(items))
        
        # Set column widths
        self.table.setColumnWidth(0, 60)  # ID column
        self.table.setColumnWidth(4, 80)  # Color column
        self.table.setColumnWidth(5, 60)  # Qty column
        self.table.setColumnWidth(9, 160)  # Actions column - slightly wider for buttons
        
        # Set row height for all rows
        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, 48)  # Increase row height for better spacing
        
        # Fonts
        regular_font = QFont("Segoe UI", 9)
        bold_font = QFont("Segoe UI", 9, QFont.Weight.Bold)
        
        for row, item in enumerate(items):
            # Populate each row with item data
            for col, value in enumerate(item):
                if col < len(item):
                    cell_item = QTableWidgetItem(str(value))
                    
                    # Make ID bold
                    if col == 0:
                        cell_item.setFont(bold_font)
                    else:
                        cell_item.setFont(regular_font)
                    
                    # Add color indicator for the Color column
                    if col == 4:  # Color column
                        try:
                            # If the color value is a recognizable color name
                            color_brush = QBrush(QColor(str(value)))
                            cell_item.setBackground(color_brush)
                            
                            # Make text white or black depending on color brightness
                            color = QColor(str(value))
                            if color.lightness() < 128:
                                cell_item.setForeground(QBrush(QColor("white")))
                        except:
                            # If color is not recognizable, just show as text
                            pass
                    
                    # Style quantity - highlight low stock
                    if col == 5:  # Qty column
                        qty = int(value) if str(value).isdigit() else 0
                        if qty <= 5:
                            cell_item.setForeground(QBrush(QColor("red")))
                            cell_item.setFont(bold_font)
                        elif qty <= 10:
                            cell_item.setForeground(QBrush(QColor("orange")))
                    
                    # Format price with currency symbol
                    if col == 6:  # Price column
                        try:
                            price = float(value)
                            cell_item.setText(f"${price:.2f}")
                        except:
                            pass
                    
                    self.table.setItem(row, col, cell_item)

            # Create Edit and Delete buttons
            button_widget = QWidget()
            button_layout = QHBoxLayout(button_widget)
            # Remove all margins to ensure buttons fit within cell boundaries
            button_layout.setContentsMargins(0, 0, 0, 0)  
            button_layout.setSpacing(4)  # Reduce spacing between buttons
            
            item_id = item[0]
            
            # Edit button - make it smaller to fit
            edit_button = StyledButton("✏️ Edit", color_scheme={
                "base": self.colors['edit'],
                "hover": self.colors['edit_hover'],
                "text": "#FFFFFF"
            })
            edit_button.setFixedWidth(75)  # Smaller width
            edit_button.setFixedHeight(32)  # Smaller height 
            edit_button.clicked.connect(lambda _, id=item_id: self.edit_item(id))
            
            # Delete button - make it smaller to fit
            delete_button = StyledButton("🗑️ Delete", color_scheme={
                "base": self.colors['delete'],
                "hover": self.colors['delete_hover'],
                "text": "#FFFFFF"
            })
            delete_button.setFixedWidth(75)  # Smaller width
            delete_button.setFixedHeight(32)  # Smaller height
            delete_button.clicked.connect(lambda _, id=item_id: self.delete_item(id))
            
            # Add buttons to layout without stretches that could push them apart
            button_layout.addWidget(edit_button)
            button_layout.addWidget(delete_button)

            # Set fixed size on the container widget to prevent expansion
            button_widget.setFixedHeight(36)

            # Add the button widget to the last column of the table
            self.table.setCellWidget(row, len(headers) - 1, button_widget)

    def edit_item(self, item_id):
        """
        Edit item with professional dialog and feedback
        """
        # Fetch the item details by ID
        item = get_item_by_id(item_id)
        if not item:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Edit Item")
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setText(f"Item with ID: {item_id} not found.")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setStyleSheet(f"""
                QMessageBox {{
                    background-color: {self.colors['background_light']};
                    color: {self.colors['text_primary']};
                }}
                QPushButton {{
                    background-color: {self.colors['primary']};
                    color: white;
                    border-radius: 4px;
                    padding: 6px 12px;
                    min-width: 80px;
                }}
                QPushButton:hover {{
                    background-color: {self.colors['primary_light']};
                }}
            """)
            msg_box.exec()
            return

        # Open the AddItemDialog pre-filled with the item's details
        dialog = AddItemDialog(self, item=item_id)
        if dialog.exec():
            # If the dialog is accepted, update the item in the database
            updated_item = dialog.get_item_data()
            update_item_in_db(item_id, updated_item)
            
            # Success message
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Success")
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setText(f"Item with ID: {item_id} updated successfully.")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setStyleSheet(f"""
                QMessageBox {{
                    background-color: {self.colors['background_light']};
                    color: {self.colors['text_primary']};
                }}
                QPushButton {{
                    background-color: {self.colors['primary']};
                    color: white;
                    border-radius: 4px;
                    padding: 6px 12px;
                    min-width: 80px;
                }}
                QPushButton:hover {{
                    background-color: {self.colors['primary_light']};
                }}
            """)
            msg_box.exec()
            
            self.load_items()  # Reload the table to reflect the changes

    def delete_item(self, item_id):
        """
        Delete item with confirmation and animation
        """
        # Create custom confirmation dialog
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Delete")
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setText(f"Are you sure you want to delete item with ID: {item_id}?")
        msg_box.setInformativeText("This action cannot be undone.")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {self.colors['background_light']};
                color: {self.colors['text_primary']};
            }}
            QPushButton {{
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 80px;
            }}
            QPushButton[text="Yes"] {{
                background-color: {self.colors['delete']};
                color: white;
            }}
            QPushButton[text="Yes"]:hover {{
                background-color: {self.colors['delete_hover']};
            }}
            QPushButton[text="No"] {{
                background-color: {self.colors['background_alt']};
                color: {self.colors['text_primary']};
                border: 1px solid {self.colors['border']};
            }}
            QPushButton[text="No"]:hover {{
                background-color: {self.colors['background']};
            }}
        """)
        
        reply = msg_box.exec()

        if reply == QMessageBox.StandardButton.Yes:
            # Perform the deletion logic
            delete_item_from_db(item_id)  # Delete the item from the database
            
            # Success message
            success_box = QMessageBox(self)
            success_box.setWindowTitle("Success")
            success_box.setIcon(QMessageBox.Icon.Information)
            success_box.setText(f"Item with ID: {item_id} deleted successfully.")
            success_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            success_box.setStyleSheet(f"""
                QMessageBox {{
                    background-color: {self.colors['background_light']};
                    color: {self.colors['text_primary']};
                }}
                QPushButton {{
                    background-color: {self.colors['primary']};
                    color: white;
                    border-radius: 4px;
                    padding: 6px 12px;
                    min-width: 80px;
                }}
                QPushButton:hover {{
                    background-color: {self.colors['primary_light']};
                }}
            """)
            success_box.exec()
            
            self.load_items()  # Reload the table to reflect the changes

    def show_add_dialog(self):
        """
        Display dialog to add a new item
        """
        dialog = AddItemDialog(self)
        if dialog.exec():
            new_item = dialog.get_item_data()
            add_item_to_db(new_item)
            
            # Success message
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Success")
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setText("New item added successfully.")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setStyleSheet(f"""
                QMessageBox {{
                    background-color: {self.colors['background_light']};
                    color: {self.colors['text_primary']};
                }}
                QPushButton {{
                    background-color: {self.colors['primary']};
                    color: white;
                    border-radius: 4px;
                    padding: 6px 12px;
                    min-width: 80px;
                }}
                QPushButton:hover {{
                    background-color: {self.colors['primary_light']};
                }}
            """)
            msg_box.exec()
            
            self.load_items()