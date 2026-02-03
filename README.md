Secure Print: Smart Shop Terminal
A professional Flask-based print management system that allows customers to "drop" files to a shop terminal via manual upload or a QR-based Scan-to-Drop feature.

🚀 Key Features
Step-by-Step Customer UI: A guided interface where options (Color Mode, Copies) only appear after a document is selected.

Scan-to-Drop: Customers can scan a shop-specific QR code to instantly send their document to the terminal.

Duplicate & Replica Prevention: A server-side "Time-Lock" ensures that if a scanner sends the same file multiple times, only one unique print job is created while still showing the customer their correct token.

Real-Time Shop Dashboard: Shopkeepers see a live queue with file formats (PDF, JPG, PNG), color settings, and a 10-minute auto-expiry timer.

Direct Browser Printing: Integrated "Print" button that triggers the native browser print dialog without requiring a file download.

Audit Logging: Every transaction is logged into a print_shop_logs.csv file with timestamps, filenames, and pickup codes for end-of-day reconciliation.

🛠️ Technical Implementation
Duplicate Lock Logic
To handle high-speed scanners that might trigger multiple requests, the system uses a global recent_scans tracker. It stores the (timestamp, pickup_code) for every unique scan. If a duplicate arrives within 10 seconds, the system fetches the existing code instead of creating a new database entry.

Progressive Disclosure UI
The frontend uses Tailwind CSS and JavaScript to manage state. The proOptions container is hidden by default and only transitions to display: block once the fileInput detects a selected document.

📁 Project Structure
main.py: The Flask backend containing the duplicate prevention logic and print queue management.

upload.html: The customer-facing step-by-step upload and scan interface.

dashboard.html: The shopkeeper’s terminal for managing active print jobs.

home.html: An administrative view showing total prints today and audit logs.

🔧 Setup
Install Requirements: Ensure Flask and SQLAlchemy are installed.

Initialize Database: The system automatically creates print_service.db on the first run.

Run the Server:
Bash
python main.py

Access Terminal:
Customer Upload: http://localhost:5000/
Shop Dashboard: http://localhost:5000/shop

Customer Upload: http://localhost:5000/

Shop Dashboard: http://localhost:5000/shop
