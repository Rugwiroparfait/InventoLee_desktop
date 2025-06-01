from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
                              QTableWidgetItem, QLabel, QComboBox, QDateEdit, QMessageBox,
                              QFrame, QHeaderView, QSpinBox, QDoubleSpinBox, QDialog, QFormLayout,
                              QLineEdit, QTabWidget, QStackedWidget, QSplitter, QCheckBox)
from PySide6.QtGui import QFont, QColor, QBrush
from PySide6.QtCore import Qt, QDate
from datetime import datetime, timedelta
from app.models.sales import add_sale, get_all_sales, get_summary, delete_last_sale, delete_all_sales
from app.models.inventory import get_all_items, get_item_by_id
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from app.ui.google_sheets_dialog import GoogleSheetsDialog
from app.utils.google_sheets_sync import GoogleSheetsSync

class AddSaleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Sale")
        self.setMinimumWidth(400)
        
        # Get inventory items for dropdown
        self.items = get_all_items()
        
        # Store the purchase price (from inventory)
        self.purchase_price = 0.0
        
        layout = QFormLayout()
        self.setLayout(layout)
        
        # Date selection
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        layout.addRow("Date:", self.date_edit)
        
        # Item selection - update the displayed text to include description instead of color
        self.item_combo = QComboBox()
        for item in self.items:
            self.item_combo.addItem(f"{item[1]} - {item[4]} (ID: {item[0]}, Stock: {item[5]}, Cost: ${item[6]:.2f})", item[0])
        self.item_combo.currentIndexChanged.connect(self.update_price)
        layout.addRow("Item:", self.item_combo)
        
        # Quantity
        self.quantity = QSpinBox()
        self.quantity.setMinimum(1)
        self.quantity.setMaximum(999)
        self.quantity.valueChanged.connect(self.calculate_total)
        layout.addRow("Quantity:", self.quantity)
        
        # Purchase price display (read-only)
        self.purchase_price_display = QDoubleSpinBox()
        self.purchase_price_display.setMinimum(0.0)
        self.purchase_price_display.setMaximum(9999.99)
        self.purchase_price_display.setDecimals(2)
        self.purchase_price_display.setReadOnly(True)
        self.purchase_price_display.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        self.purchase_price_display.setStyleSheet("background-color: #ECE8E3;")
        layout.addRow("Purchase Price ($):", self.purchase_price_display)
        
        # Selling price (what the customer pays)
        self.price = QDoubleSpinBox()
        self.price.setMinimum(0.01)
        self.price.setMaximum(9999.99)
        self.price.setDecimals(2)
        self.price.valueChanged.connect(self.calculate_total)
        layout.addRow("Selling Price ($):", self.price)
        
        # Add pricing information labels
        purchase_info = QLabel("↑ This is what you paid for the item (from inventory)")
        purchase_info.setStyleSheet("color: #6B717E; font-size: 9pt; font-style: italic;")
        layout.addRow("", purchase_info)
        
        selling_info = QLabel("↑ This is what the customer will pay")
        selling_info.setStyleSheet("color: #6B717E; font-size: 9pt; font-style: italic;")
        layout.addRow("", selling_info)
        
        # Total amount (calculated)
        self.total = QDoubleSpinBox()
        self.total.setMinimum(0.01)
        self.total.setMaximum(999999.99)
        self.total.setDecimals(2)
        self.total.setReadOnly(True)
        self.total.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        layout.addRow("Total Amount ($):", self.total)
        
        # Payment method
        self.payment_method = QComboBox()
        self.payment_method.addItems(["Cash", "Card", "Mobile Money", "Bank Transfer", "Other"])
        layout.addRow("Payment Method:", self.payment_method)
        
        # Profit (calculated automatically)
        self.profit = QDoubleSpinBox()
        self.profit.setMinimum(-9999.99)  # Allow negative for losses
        self.profit.setMaximum(9999.99)
        self.profit.setDecimals(2)
        self.profit.setReadOnly(True)
        self.profit.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        layout.addRow("Profit ($):", self.profit)
        
        # Auto-calculate profit checkbox
        self.auto_calculate_checkbox = QCheckBox("Auto-calculate profit")
        self.auto_calculate_checkbox.setChecked(True)
        self.auto_calculate_checkbox.stateChanged.connect(self.toggle_profit_edit)
        layout.addRow("", self.auto_calculate_checkbox)
        
        # Notes
        self.notes = QLineEdit()
        layout.addRow("Notes:", self.notes)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Sale")
        self.cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addRow("", button_layout)
        
        # Connect signals
        self.save_btn.clicked.connect(self.save_sale)
        self.cancel_btn.clicked.connect(self.reject)
        
        # Initialize with first item
        self.update_price()
    
    def toggle_profit_edit(self, state):
        """Toggle whether profit is auto-calculated or manually entered"""
        is_auto = state == Qt.CheckState.Checked.value
        self.profit.setReadOnly(is_auto)
        self.profit.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons if is_auto else QDoubleSpinBox.ButtonSymbols.UpDownArrows)
        
        # Update calculation if turning auto back on
        if is_auto:
            self.calculate_total()
    
    def update_price(self):
        """Update prices when item selection changes"""
        # Get selected item ID
        item_id = self.item_combo.currentData()
        if item_id:
            item = get_item_by_id(item_id)
            if item and len(item) > 6:
                # Store the purchase price from inventory
                self.purchase_price = item[6]
                self.purchase_price_display.setValue(self.purchase_price)
                
                # Set initial selling price to match purchase price (can be adjusted)
                self.price.setValue(item[6] * 1.3)  # Default 30% markup
                
                # Calculate total and profit
                self.calculate_total()
    
    def calculate_total(self):
        """Calculate total amount and profit"""
        quantity = self.quantity.value()
        selling_price = self.price.value()
        total = quantity * selling_price
        self.total.setValue(total)
        
        # Calculate profit if auto-calculate is checked
        if self.auto_calculate_checkbox.isChecked():
            # Profit = (Selling Price - Purchase Price) × Quantity
            profit = (selling_price - self.purchase_price) * quantity
            self.profit.setValue(profit)
    
    def save_sale(self):
        """Save the sale to the database"""
        # Get the selected item ID
        item_id = self.item_combo.currentData()
        
        # Check if there's enough inventory
        item = get_item_by_id(item_id)
        if not item or self.quantity.value() > item[5]:
            QMessageBox.warning(self, "Insufficient Stock", 
                               "The requested quantity exceeds available stock.")
            return
        
        # Prepare sale data
        sale_data = {
            'date': self.date_edit.date().toString("yyyy-MM-dd"),
            'item_id': item_id,
            'quantity': self.quantity.value(),
            'unit_price': self.price.value(),
            'total_amount': self.total.value(),
            'payment_method': self.payment_method.currentText(),
            'profit': self.profit.value(),
            'expense_notes': self.notes.text()
        }
        
        try:
            # Add sale to database
            add_sale(sale_data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save sale: {str(e)}")


class SalesView(QWidget):
    def __init__(self):
        super().__init__()
        
        # Set up theme and colors (similar to inventory view)
        self.setup_ui_theme()
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)
        
        # Header section
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel("Daily Sales Book")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {self.colors['primary']};")
        
        subtitle_label = QLabel("Track your sales, profits, and bestselling items")
        subtitle_label.setFont(QFont("Segoe UI", 10))
        subtitle_label.setStyleSheet(f"color: {self.colors['text_secondary']};")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        main_layout.addWidget(header_frame)
        
        # Tabs for sales table and summary
        self.tabs = QTabWidget()
        
        # Sales table tab
        self.sales_table_widget = QWidget()
        self.setup_sales_table()
        self.tabs.addTab(self.sales_table_widget, "📝 Sales Log")
        
        # Summary tab
        self.summary_widget = QWidget()
        self.setup_summary_tab()
        self.tabs.addTab(self.summary_widget, "📊 Profit & Loss")
        
        main_layout.addWidget(self.tabs)
    
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
    
    def setup_sales_table(self):
        layout = QVBoxLayout(self.sales_table_widget)
        
        # Controls for filtering and adding new sales
        controls_frame = QFrame()
        controls_frame.setStyleSheet(f"""
            background-color: {self.colors['background_light']};
            border-radius: 8px;
            padding: 8px;
        """)
        
        controls_layout = QHBoxLayout(controls_frame)
        
        # Date range selection
        date_label = QLabel("Date Range:")
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))  # Last 30 days
        self.start_date.setCalendarPopup(True)
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        
        filter_btn = QPushButton("Filter")
        filter_btn.clicked.connect(self.load_sales)
        
        # Add sale button
        add_sale_btn = QPushButton("➕ Add Sale")
        add_sale_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['primary']};
                color: white;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.colors['primary_light']};
            }}
            QPushButton:pressed {{
                padding: 9px 15px 7px 17px;
            }}
        """)
        add_sale_btn.clicked.connect(self.show_add_sale_dialog)
        
        # Clear last entry button
        clear_last_btn = QPushButton("🗑️ Clear Last Entry")
        clear_last_btn.setStyleSheet(f"""
            background-color: {self.colors['delete']};
            color: white;
            border-radius: 4px;
            padding: 6px 12px;
        """)
        clear_last_btn.clicked.connect(self.clear_last_entry)
        
        # Clear all button
        clear_all_btn = QPushButton("🗑️ Clear All")
        clear_all_btn.setStyleSheet(f"""
            background-color: {self.colors['delete']};
            color: white;
            border-radius: 4px;
            padding: 6px 12px;
        """)
        clear_all_btn.clicked.connect(self.clear_all_entries)
        
        # Google Sheets sync button
        sheets_btn = QPushButton("🔄 Sync to Sheets")
        sheets_btn.setStyleSheet(f"""
            background-color: {self.colors['secondary']};
            color: white;
            border-radius: 4px;
            padding: 6px 12px;
""")
        sheets_btn.clicked.connect(self.sync_sales_to_sheets)
        
        controls_layout.addWidget(date_label)
        controls_layout.addWidget(self.start_date)
        controls_layout.addWidget(QLabel("to"))
        controls_layout.addWidget(self.end_date)
        controls_layout.addWidget(filter_btn)
        controls_layout.addStretch()
        controls_layout.addWidget(add_sale_btn)
        controls_layout.addWidget(clear_last_btn)
        controls_layout.addWidget(clear_all_btn)
        controls_layout.addWidget(sheets_btn)
        
        layout.addWidget(controls_frame)
        
        # Sales table
        table_frame = QFrame()
        table_frame.setStyleSheet(f"""
            background-color: {self.colors['background_light']};
            border-radius: 8px;
            padding: 1px;
        """)
        
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(5, 5, 5, 5)
        
        self.sales_table = QTableWidget()
        self.sales_table.setAlternatingRowColors(True)
        self.sales_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.sales_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.sales_table.horizontalHeader().setStretchLastSection(True)
        self.sales_table.verticalHeader().setVisible(False)
        
        # Styling
        self.sales_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {self.colors['background_light']};
                alternate-background-color: {self.colors['background_alt']};
                border: none;
                border-radius: 8px;
                gridline-color: {self.colors['border']};
            }}
            
            QTableWidget::item {{
                padding: 12px 8px;
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
                padding: 12px;
                border: none;
                border-bottom: 2px solid {self.colors['primary']};
                border-right: 1px solid {self.colors['border']};
            }}
        """)
        
        table_layout.addWidget(self.sales_table)
        
        # Status label for totals
        self.status_label = QLabel()
        self.status_label.setStyleSheet(f"color: {self.colors['text_secondary']}; padding: 8px;")
        table_layout.addWidget(self.status_label)
        
        layout.addWidget(table_frame)
        
        # Load initial data
        self.load_sales()
        
    def setup_summary_tab(self):
        layout = QVBoxLayout(self.summary_widget)
        
        # Add metric cards at the top
        cards_frame = self.add_summary_cards()
        layout.addWidget(cards_frame)
    
        # Controls for summary period
        controls_frame = QFrame()
        controls_frame.setStyleSheet(f"""
            background-color: {self.colors['background_light']};
            border-radius: 8px;
            padding: 8px;
        """)
        
        controls_layout = QHBoxLayout(controls_frame)
        
        period_label = QLabel("Summary Period:")
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Daily", "Weekly", "Monthly"])
        self.period_combo.currentTextChanged.connect(lambda: self.load_summary())
        
        # Date range for summary
        self.summary_start_date = QDateEdit()
        self.summary_start_date.setDate(QDate.currentDate().addDays(-30))
        self.summary_start_date.setCalendarPopup(True)
        self.summary_start_date.dateChanged.connect(lambda: self.load_summary())
        
        self.summary_end_date = QDateEdit()
        self.summary_end_date.setDate(QDate.currentDate())
        self.summary_end_date.setCalendarPopup(True)
        self.summary_end_date.dateChanged.connect(lambda: self.load_summary())
        
        controls_layout.addWidget(period_label)
        controls_layout.addWidget(self.period_combo)
        controls_layout.addWidget(QLabel("From:"))
        controls_layout.addWidget(self.summary_start_date)
        controls_layout.addWidget(QLabel("To:"))
        controls_layout.addWidget(self.summary_end_date)
        controls_layout.addStretch()
        
        layout.addWidget(controls_frame)
        
        # Split view: table on top, charts below
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Summary table section 
        table_frame = QFrame()
        table_frame.setStyleSheet(f"""
            background-color: {self.colors['background_light']};
            border-radius: 8px;
            padding: 1px;
        """)
        
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(5, 5, 5, 5)
        
        self.summary_table = QTableWidget()
        self.summary_table.setAlternatingRowColors(True)
        self.summary_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.summary_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.summary_table.horizontalHeader().setStretchLastSection(True)
        self.summary_table.verticalHeader().setVisible(False)
        
        # Apply same styling as sales table
        self.summary_table.setStyleSheet(self.sales_table.styleSheet())
        
        table_layout.addWidget(self.summary_table)
        layout.addWidget(table_frame)
        
        # Add visualization charts section
        charts_frame = self.setup_summary_charts()
        
        # Add both to splitter
        splitter.addWidget(table_frame)
        splitter.addWidget(charts_frame)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)  # Charts get more space
        
        layout.addWidget(splitter)
        
        # Load initial summary
        self.load_summary()
    
    def setup_summary_charts(self):
        """Create and display charts for sales data visualization"""
        # Create chart frame
        chart_frame = QFrame()
        chart_frame.setStyleSheet(f"""
            background-color: {self.colors['background_light']};
            border-radius: 8px;
            padding: 8px;
        """)
        chart_layout = QHBoxLayout(chart_frame)
        
        # Create figure with two subplots
        self.figure = Figure(figsize=(10, 5), facecolor=self.colors['background_light'])
        self.figure.subplots_adjust(bottom=0.15, wspace=0.3)
        self.canvas = FigureCanvasQTAgg(self.figure)
        
        # Add canvas to layout
        chart_layout.addWidget(self.canvas)
        
        # Return the frame to be added to main layout
        return chart_frame

    def update_charts(self, summaries):
        """Update charts with the latest summary data"""
        if not summaries:
            return
            
        self.figure.clear()
        
        # Extract data
        periods = [s[0] for s in summaries]
        sales = [s[1] for s in summaries]
        profits = [s[2] for s in summaries]
        
        # Create two subplots
        ax1 = self.figure.add_subplot(121)  # Sales trend
        ax2 = self.figure.add_subplot(122)  # Profit margin
        
        # Format both axes
        for ax in [ax1, ax2]:
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.tick_params(axis='x', rotation=45)
            ax.set_facecolor(self.colors['background_light'])
        
        # Sales trend chart
        bars = ax1.bar(periods, sales, color=self.colors['primary'])
        ax1.set_title('Sales Trend', fontweight='bold', fontsize=12, color=self.colors['text_primary'])
        ax1.set_ylabel('Total Sales ($)', color=self.colors['text_secondary'])
        ax1.tick_params(colors=self.colors['text_secondary'])

        # Add value labels to the sales bars too
        for bar in bars:
            height = bar.get_height()
            ax1.annotate(f'${height:.0f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=8)

        # Profit margin chart
        margins = [(p/s*100) if s > 0 else 0 for p, s in zip(profits, sales)]
        colors = [self.colors['profit'] if m >= 0 else self.colors['loss'] for m in margins]
        
        bars2 = ax2.bar(periods, margins, color=colors)
        ax2.set_title('Profit Margin (%)', fontweight='bold', fontsize=12)
        ax2.set_ylabel('Margin %')
        
        # Add value labels
        for bar in bars2:
            height = bar.get_height()
            ax2.annotate(f'{height:.1f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=8)
        
        # Set better background color for chart
        self.figure.set_facecolor(self.colors['background'])
        for ax in [ax1, ax2]:
            ax.set_facecolor(self.colors['background_light'])
            ax.spines['bottom'].set_color(self.colors['border'])
            ax.spines['left'].set_color(self.colors['border'])
            ax.tick_params(colors=self.colors['text_secondary'])
        
        # Refresh canvas
        self.canvas.draw()
    
    def load_sales(self):
        # Get date range
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        
        # Load sales data
        sales = get_all_sales(start_date, end_date)
        
        # Set up table
        headers = ["ID", "Date", "Item", "Quantity", "Unit Price", "Total", "Payment Method", "Profit", "Notes"]
        self.sales_table.setColumnCount(len(headers))
        self.sales_table.setHorizontalHeaderLabels(headers)
        self.sales_table.setRowCount(len(sales))
        
        # Set column widths
        self.sales_table.setColumnWidth(0, 50)   # ID
        self.sales_table.setColumnWidth(1, 100)  # Date
        self.sales_table.setColumnWidth(2, 180)  # Item
        self.sales_table.setColumnWidth(3, 80)   # Quantity
        self.sales_table.setColumnWidth(4, 100)  # Unit Price
        self.sales_table.setColumnWidth(5, 100)  # Total
        self.sales_table.setColumnWidth(6, 130)  # Payment Method
        self.sales_table.setColumnWidth(7, 100)  # Profit
        
        # Fonts
        regular_font = QFont("Segoe UI", 9)
        bold_font = QFont("Segoe UI", 9, QFont.Weight.Bold)
        
        # Fill table with data
        for row, sale in enumerate(sales):
            for col, value in enumerate(sale):
                if value is None:
                    value = ""
                
                cell_item = QTableWidgetItem(str(value))
                
                # ID in bold
                if col == 0:
                    cell_item.setFont(bold_font)
                else:
                    cell_item.setFont(regular_font)
                
                # Format prices with $ symbol
                if col in [4, 5, 7]:  # Unit price, Total, Profit columns
                    try:
                        amount = float(value)
                        cell_item.setText(f"${amount:.2f}")
                        
                        # Color profit/loss
                        if col == 7 and value != "":
                            if amount >= 0:
                                cell_item.setForeground(QBrush(QColor(self.colors['profit'])))
                            else:
                                cell_item.setForeground(QBrush(QColor(self.colors['loss'])))
                    except:
                        pass
                
                self.sales_table.setItem(row, col, cell_item)
            
        # After creating the rows, set fixed row heights for uniformity
        for row in range(self.sales_table.rowCount()):
            self.sales_table.setRowHeight(row, 48)
        
        # Show totals in status bar
        total_sales = sum(sale[5] for sale in sales) if sales else 0
        total_profit = sum(sale[7] for sale in sales if sale[7] is not None) if sales else 0
    
        # Display totals in the status label
        self.status_label.setStyleSheet(f"""
            color: {self.colors['text_primary']}; 
            padding: 12px;
            background-color: {self.colors['background_alt']};
            border-top: 1px solid {self.colors['border']};
            border-radius: 0px 0px 8px 8px;
            font-weight: bold;
        """)
        
        # Add icons to the status message
        self.status_label.setText(
            f"📊 Summary: {len(sales)} sales  |  💰 Total Revenue: ${total_sales:.2f}  |  "
            f"{'📈' if total_profit >= 0 else '📉'} Total Profit: ${total_profit:.2f}"
        )
        
    def load_summary(self):
        # Get date range
        start_date = self.summary_start_date.date().toString("yyyy-MM-dd")
        end_date = self.summary_end_date.date().toString("yyyy-MM-dd")
        
        # Get period type
        period_type = self.period_combo.currentText().lower()
        
        # Load summary data
        summaries = get_summary(period_type, start_date, end_date)
        
        # Set up table
        headers = ["Period", "Total Sales", "Total Profit", "Profit Margin %"]
        self.summary_table.setColumnCount(len(headers))
        self.summary_table.setHorizontalHeaderLabels(headers)
        self.summary_table.setRowCount(len(summaries))
        
        # Set column widths
        self.summary_table.setColumnWidth(0, 120)  # Period
        self.summary_table.setColumnWidth(1, 120)  # Total Sales
        self.summary_table.setColumnWidth(2, 120)  # Total Profit
        self.summary_table.setColumnWidth(3, 120)  # Margin
        
        # Fill table with data
        for row, summary in enumerate(summaries):
            period, total_sales, total_profit = summary
            
            # Period
            period_item = QTableWidgetItem(period)
            self.summary_table.setItem(row, 0, period_item)
            
            # Total Sales
            sales_item = QTableWidgetItem(f"${total_sales:.2f}")
            self.summary_table.setItem(row, 1, sales_item)
            
            # Total Profit
            profit_item = QTableWidgetItem(f"${total_profit:.2f}")
            if total_profit >= 0:
                profit_item.setForeground(QBrush(QColor(self.colors['profit'])))
            else:
                profit_item.setForeground(QBrush(QColor(self.colors['loss'])))
            self.summary_table.setItem(row, 2, profit_item)
            
            # Profit Margin %
            margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
            margin_item = QTableWidgetItem(f"{margin:.1f}%")
            if margin >= 0:
                margin_item.setForeground(QBrush(QColor(self.colors['profit'])))
            else:
                margin_item.setForeground(QBrush(QColor(self.colors['loss'])))
            self.summary_table.setItem(row, 3, margin_item)
            
        # After populating the summary table, update cards and charts
    
        # Calculate totals for cards
        total_sales = sum(summary[1] for summary in summaries) if summaries else 0
        total_profit = sum(summary[2] for summary in summaries) if summaries else 0
        avg_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
        
        # Update cards
        self.card_values["sales"].setText(f"${total_sales:.2f}")
        self.card_values["profit"].setText(f"${total_profit:.2f}")
        self.card_values["margin"].setText(f"{avg_margin:.1f}%")
        
        # Update subtitles
        period_type = self.period_combo.currentText()
        date_range = f"{self.summary_start_date.date().toString('MMM d')} - {self.summary_end_date.date().toString('MMM d, yyyy')}"
        for key in ["sales_subtitle", "profit_subtitle", "margin_subtitle"]:
            self.card_values[key].setText(f"{period_type} totals • {date_range}")
        
        # Update charts
        self.update_charts(summaries)
    
    def add_summary_cards(self):
        """Add elegant info cards at the top of summary tab"""
        # Create frame for cards
        cards_frame = QFrame()
        cards_layout = QHBoxLayout(cards_frame)
        cards_layout.setSpacing(15)
        
        # Card style template
        card_style = lambda color: f"""
            QFrame {{
                background-color: {self.colors['background_light']};
                border-left: 6px solid {color};
                border-radius: 6px;
                padding: 10px;
            }}
            QLabel[objectName^="title"] {{
                font-size: 13px;
                font-weight: bold;
                color: {self.colors['text_primary']};
            }}
            QLabel[objectName^="value"] {{
                font-size: 24px;
                font-weight: bold;
                color: {color};
            }}
            QLabel[objectName^="subtitle"] {{
                font-size: 11px;
                color: {self.colors['text_secondary']};
            }}
        """
        
        # Create cards for key metrics
        metrics = [
            {"title": "Total Sales", "color": self.colors['primary'], "id": "sales"},
            {"title": "Total Profit", "color": self.colors['profit'], "id": "profit"},
            {"title": "Average Margin", "color": self.colors['secondary'], "id": "margin"}
        ]
        
        for metric in metrics:
            # Create card frame
            card = QFrame()
            card.setObjectName(f"card_{metric['id']}")
            card.setStyleSheet(card_style(metric['color']))
            card.setMinimumWidth(200)
            card.setMinimumHeight(120)
            
            # Card layout
            card_layout = QVBoxLayout(card)
            
            # Card content
            title = QLabel(metric['title'])
            title.setObjectName(f"title_{metric['id']}")
            
            value = QLabel("$0")
            value.setObjectName(f"value_{metric['id']}")
            value.setAlignment(Qt.AlignmentFlag.AlignLeft)
            
            subtitle = QLabel("No data available")
            subtitle.setObjectName(f"subtitle_{metric['id']}")
            
            # Add to layout
            card_layout.addWidget(title)
            card_layout.addWidget(value)
            card_layout.addWidget(subtitle)
            card_layout.addStretch()
            
            # Add card to row
            cards_layout.addWidget(card)
        
        # Store references to value labels for updating
        self.card_values = {
            "sales": cards_frame.findChild(QLabel, "value_sales"),
            "profit": cards_frame.findChild(QLabel, "value_profit"),
            "margin": cards_frame.findChild(QLabel, "value_margin"),
            "sales_subtitle": cards_frame.findChild(QLabel, "subtitle_sales"),
            "profit_subtitle": cards_frame.findChild(QLabel, "subtitle_profit"),
            "margin_subtitle": cards_frame.findChild(QLabel, "subtitle_margin"),
        }
        
        return cards_frame
    
    def show_add_sale_dialog(self):
        """Display dialog to add a new sale"""
        dialog = AddSaleDialog(self)
        if dialog.exec():
            # Refresh the sales view after adding a sale
            self.load_sales()
            
            # Show success message
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Success")
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setText("New sale added successfully.")
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
                    padding: 8px 15px;
                    min-width: 85px;
                }}
                QPushButton:hover {{
                    background-color: {self.colors['primary_light']};
                }}
            """)
            msg_box.exec()

    def clear_last_entry(self):
        """Clear the last sales entry and restore inventory"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Delete")
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setText("Are you sure you want to delete the last sale entry?")
        msg_box.setInformativeText("This will restore the items to inventory.")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        # Apply styling
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
        """)
        
        reply = msg_box.exec()
        if reply == QMessageBox.StandardButton.Yes:
            success = delete_last_sale()
            
            if success:
                # Show success message
                QMessageBox.information(self, "Success", "Last sale entry deleted successfully.")
                
                # Refresh both tables
                self.load_sales()
                if hasattr(self, 'load_summary'):
                    self.load_summary()
            else:
                QMessageBox.warning(self, "Warning", "No sales found to delete.")

    def clear_all_entries(self):
        """Clear all sales entries (with strong warning)"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("⚠️ CAUTION: Delete All Sales")
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setText("Are you ABSOLUTELY SURE you want to delete ALL sales data?")
        msg_box.setInformativeText("This action CANNOT be undone and will NOT restore inventory!")
        
        # Add text input for confirmation
        from PySide6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, "Confirm Deletion", 
                                       "Type 'DELETE' to confirm deletion of all sales:")
        
        if ok and text == "DELETE":
            success = delete_all_sales()
            
            if success:
                # Show success message
                QMessageBox.information(self, "Success", "All sales data has been deleted.")
                
                # Refresh both tables
                self.load_sales()
                if hasattr(self, 'load_summary'):
                    self.load_summary()
        elif ok:
            QMessageBox.warning(self, "Cancelled", "Delete operation cancelled - confirmation text didn't match.")
    
    def sync_sales_to_sheets(self):
        """Sync current filtered sales data to Google Sheets"""
        # Get current date range
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        
        # Initialize Google Sheets sync
        sheets_sync = GoogleSheetsSync()
        
        if not sheets_sync.is_configured():
            # Show settings dialog if not configured
            dialog = GoogleSheetsDialog(self)
            result = dialog.exec()
            if result != QDialog.DialogCode.Accepted:
                return
            
            # Reinitialize with new settings
            sheets_sync = GoogleSheetsSync()
        
        # Sync data
        success, message = sheets_sync.sync_sales(start_date, end_date)
        
        if success:
            QMessageBox.information(self, "Sync Successful", message)
        else:
            QMessageBox.warning(self, "Sync Failed", message)