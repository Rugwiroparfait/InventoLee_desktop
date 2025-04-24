#  InventoLee App Structure/Architecture


inventolee_desktop/
├── app/
│   ├── __init__.py
│   ├── db.py                  # Database initialization and connection
│   ├── models/                # Data models & DB operations
│   │   ├── inventory.py       # Logic for items (add, update, delete)
│   │   ├── transactions.py    # Logic for manual transactions
│   │   └── reports.py         # Generate CSV/PDFs
│   ├── ui/                    # All GUI components
│   │   ├── main_window.py     # MainWindow layout (dashboard shell)
│   │   ├── dashboard.py       # Graphs and stats
│   │   ├── inventory_view.py  # Table and filters
│   │   ├── item_form.py       # Add/edit item dialog
│   │   ├── transaction_log.py # Record + view manual ops
│   │   └── alerts.py          # Notifications for missing stock
│   ├── utils/                 # Helpers
│   │   ├── export.py          # CSV/PDF helpers
│   │   └── charting.py        # Wrap matplotlib or pyqtgraph
│   └── constants.py           # Field names, app title, thresholds
├── assets/                    # Icons, logo, styling
├── resources/
│   └── style.qss              # Qt stylesheet (optional)
├── main.py                    # App launcher
├── requirements.txt
└── README.md



## Modules & Their Roles

Module : Responsibility
db.py : Connect/init SQLite DB
models/inventory.py : Add/edit/delete items
models/transactions.py : Record and read transactions
models/reports.py : Generate reports
ui/main_window.py : Brings together dashboard + inventory + transactions
ui/dashboard.py : Display stats and graphs
ui/inventory_view.py : Table view with filters
ui/item_form.py : Form for adding/editing inventory
ui/transaction_log.py : Form/table for logging manual operations
ui/alerts.py : Checks and notifies about low stock
utils/export.py : CSV/PDF exports
utils/charting.py : Reusable charting logic
constants.py : Reorder thresholds, app metadata, etc.