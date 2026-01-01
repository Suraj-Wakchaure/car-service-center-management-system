# 🚗 Car Service Center Management System

A desktop-based application developed using **Python, Tkinter, and SQLite** to efficiently manage day-to-day operations of a car service center.  
The system automates customer handling, vehicle records, job cards, parts inventory, invoicing, and report generation with role-based access.

---

## ✨ Key Features

- 🔐 **Role-Based Login**
  - Admin: Full access to all modules and reports
  - Receptionist: Limited operational access

- 👤 **Customer Management**
  - Add, update, view, and manage customer details

- 🚘 **Vehicle Management**
  - Maintain vehicle records linked to customers

- 🧾 **Job Card Management**
  - Create and track service job cards

- 🛠️ **Parts Inventory**
  - Manage spare parts and stock availability

- 💰 **Invoice Generation**
  - Automated invoice creation based on services and parts used

- 📊 **Reports**
  - Text-based administrative reports for analysis

---

## 🧠 Tech Stack

- **Programming Language:** Python  
- **GUI Framework:** Tkinter  
- **Database:** SQLite  
- **Architecture:** Modular, database-driven design 

---

## 📂 Project Structure
```text
car-service-center-management-system/
│
├── auto_run.py               # Application entry point
├── requirements.txt          # Project dependencies
├── README.md                 # Project documentation
├── .gitignore                # Git ignore rules
│
├── database/
│   ├── database.py           # Database connection & queries
│   └── car_service.db        # SQLite database
│
├── ui/
│   ├── login_page.py         # User authentication
│   ├── main_window.py        # Dashboard / main window
│   ├── customers_page.py    # Customer management
│   ├── vehicles_page.py     # Vehicle records
│   ├── jobs_page.py          # Service jobs
│   ├── job_cards_page.py    # Job card handling
│   ├── parts_page.py         # Parts inventory
│   ├── invoices_page.py     # Billing & invoices
│   └── reports_page.py      # Report generation
│
├── docs/
│   ├── ER_Diagram.png        # Entity Relationship diagram
│   ├── Class_Diagram.png     # Class diagram
│   ├── Use_Case_Diagram.png  # Use case diagram
│   └── Activity_Diagram.png  # Activity diagram
│
└── reports/
    └── sample_reports.txt    # Sample generated reports


