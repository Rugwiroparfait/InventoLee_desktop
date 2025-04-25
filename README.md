# 🧾 InventoLee Desktop App

**InventoLee** is a lightweight, modular inventory management desktop application designed using Python and PyQt. It offers intuitive GUI features for managing inventory, visualizing stats, generating reports, and tracking transactions — all in one sleek package.

---

## 📁 Project Structure

```
inventolee_desktop/
├── app/
│   ├── __init__.py
│   ├── db.py
│   ├── models/
│   │   ├── inventory.py
│   │   ├── transactions.py
│   │   └── reports.py
│   ├── ui/
│   │   ├── main_window.py
│   │   ├── dashboard.py
│   │   ├── inventory_view.py
│   │   ├── item_form.py
│   │   ├── transaction_log.py
│   │   └── alerts.py
│   ├── utils/
│   │   ├── export.py
│   │   └── charting.py
│   └── constants.py
├── assets/
├── resources/
│   └── style.qss
├── main.py
├── requirements.txt
└── README.md
```

---

## 📦 Module Overview

| Module | Responsibility |
|--------|----------------|
| `db.py` | Initialize and connect to the SQLite database |
| `models/inventory.py` | CRUD operations for inventory items |
| `models/transactions.py` | Handle manual transaction records |
| `models/reports.py` | Generate inventory reports in CSV/PDF |
| `ui/main_window.py` | Main application window; integrates all UI components |
| `ui/dashboard.py` | Visual dashboard with stats and charts |
| `ui/inventory_view.py` | Table view with item filtering options |
| `ui/item_form.py` | Dialog to add or edit an inventory item |
| `ui/transaction_log.py` | Log and display manual transactions |
| `ui/alerts.py` | Notify user of low stock and missing items |
| `utils/export.py` | CSV and PDF export utilities |
| `utils/charting.py` | Graph/chart utilities using matplotlib or pyqtgraph |
| `constants.py` | Centralized app metadata and configuration constants |

---

## 💡 Features

- 🔍 **Inventory Management**: Add, edit, delete items easily.
- 📊 **Visual Dashboard**: Monitor stock levels and trends at a glance.
- 📝 **Manual Transactions**: Record non-automated changes.
- 📤 **Report Export**: Export your data in CSV or PDF formats.
- 🚨 **Low Stock Alerts**: Get notified when stocks fall below thresholds.
- 🎨 **Custom Styling**: Qt-based style sheet for UI theming.

---

## 🚀 Getting Started

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/inventolee_desktop.git
   cd inventolee_desktop
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**

   ```bash
   python main.py
   ```

---

## 🛠️ Tech Stack

- Python 3.x
- PyQt5 / PySide2
- SQLite3
- Matplotlib / PyQtGraph (for charts)
- FPDF / ReportLab (for PDFs)

---

## 📎 License

MIT License – feel free to use and modify for your personal or commercial projects.
