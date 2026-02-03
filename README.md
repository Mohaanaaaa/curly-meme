**🚀 Secure Print: Smart Terminal System**
    A professional, end-to-end print management solution designed for shops. It allows customers to "drop" documents to a local terminal via manual upload or a Smart Scan-to-Drop feature.

**📋 Key Features**
    Step-by-Step UI Flow: A clean, guided customer interface where Color Mode and Copies options only appear after a document is selected.
    Intelligent Replica Prevention: Prevents duplicate print jobs. If a scanner sends the same file multiple times, the server detects the replica, blocks a new entry, and returns the        original token to the customer.
    Live Shop Terminal: A real-time dashboard for shopkeepers featuring color-coded status badges, auto-refreshing queues, and direct browser printing.
    Automated Audit Logs: Every successful print job is recorded in a print_shop_logs.csv with original filenames and timestamps for business reconciliation.
    Auto-Cleanup Daemon: A background thread that automatically deletes files and database entries older than 10 minutes to protect customer privacy.

**🛠️ Technical Stack**
    Component Technology
    Backend      Python / Flask
    Database     SQLite / SQLAlchemy
    Frontend     Tailwind CSS / FontAwesome
    QR Scanning  Html5-QRCode
    Logging      CSV Audit Trail

**📂 Project Structure**
  main.py: The core engine handling file storage, duplicate prevention, and the print queue.
  upload.html: The customer-facing progressive disclosure interface.
  dashboard.html: The shop terminal queue with direct-print integration.
  home.html: Administrative overview showing total print volume for the day.

 ** 🔧 Installation & Setup**
   Clone the Repository:
   git clone https://github.com/your-username/secure-print.git
   cd secure-print

   Install Dependencies:
   pip install flask flask-sqlalchemy

   Run the Application:
   python main.py

   Customer Portal: http://localhost:5000/
   Shop Terminal: http://localhost:5000/shop

**🛡️ Security & Privacy**
  UUID Renaming: Every file is renamed with a unique UUID to prevent file overwriting and protect identity.
  10-Minute Expiry: Files are strictly deleted from the server 10 minutes after being uploaded.
  Duplicate Lock: A server-side recent_scans dictionary blocks rapid-fire requests from faulty scanner hardware.

  
