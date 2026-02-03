# 🚀 Secure Print Smart Terminal

A professional Flask-based print management solution for retail shops. It allows customers to "drop" documents to a local shop terminal via manual upload or a QR-based **Scan-to-Drop** feature.



## ✨ Key Features

* **Progressive Disclosure UI**: A clean step-by-step customer flow. Print options (Color, Copies) are hidden until a document is selected.
* **Intelligent Replica Prevention**: A server-side time-lock prevents duplicate print jobs from faulty scanners while ensuring the customer sees their correct token.
* **Live Shop Terminal**: A real-time queue for shopkeepers with color-coded status badges, auto-refreshing lists, and direct browser printing.
* **Auto-Cleanup**: A background daemon automatically deletes documents and database entries older than 10 minutes to protect customer privacy.
* **Audit Logging**: Every transaction is logged to `print_shop_logs.csv` for business reports.

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Backend** | Python / Flask |
| **Database** | SQLite / SQLAlchemy |
| **Frontend** | Tailwind CSS / FontAwesome |
| **QR Engine** | Html5-QRCode |

## 🔧 Setup & Installation

1. **Clone & Install**:
   ```bash
   git clone [https://github.com/your-username/secure-print.git](https://github.com/your-username/secure-print.git)
   pip install flask flask-sqlalchemy

2. **Run Server:**:
   ```bash
   python main.py
   ```
3. **Access:**
   ```bash
   Customer Portal: http://localhost:5000/
   Shop Terminal: http://localhost:5000/shop
   ```

**🛡️ Security & Privacy**

  UUID Renaming: Every file is renamed with a unique UUID to prevent file overwriting and protect identity.
  10-Minute Expiry: Files are strictly deleted from the server 10 minutes after being uploaded.
  Duplicate Lock: A server-side recent_scans dictionary blocks rapid-fire requests from faulty scanner hardware.

## 🏪 Shop-Specific QR Workflow
Each shop is assigned a unique persistent URL (`/drop/shop_id`). 
- **Scanning the Shop QR**: Directs customers to a specialized version of the UI.
- **Smart Logic**: Automatically disables internal QR scanning if a Shop ID is detected in the URL, forcing a "Drop to Shop" manual submission for better UX.
  
