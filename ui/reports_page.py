import tkinter as tk
from tkinter import ttk, messagebox
from database.database import get_conn
import datetime

class ReportsPage(tk.Frame):
    def __init__(self, root, role):
        super().__init__(root, bg="#FFFFFF")
        self.role = role

        ttk.Label(self, text="General Report", font=("Segoe UI", 14, "bold")).pack(pady=10)

        # Admin only
        if self.role == "admin":
            ttk.Button(self, text="Generate Report", command=self.display_report).pack(pady=10)
        else:
            ttk.Label(self, text="Access Denied (Admin Only)", foreground="red", bg="#FFFFFF").pack(pady=20)

        # Text area to display report
        self.report_box = tk.Text(self, width=120, height=30, font=("Consolas", 14))
        self.report_box.pack(padx=20, pady=10)
        self.report_box.config(state="disabled")  # read-only

    def display_report(self):
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) AS c FROM customers"); total_customers = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) AS c FROM vehicles"); total_vehicles = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) AS c FROM job_cards"); total_jobs = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) AS c FROM job_cards WHERE status='pending'"); pending_jobs = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) AS c FROM job_cards WHERE status='completed'"); completed_jobs = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) AS c FROM invoices"); total_invoices = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) AS c FROM invoices WHERE payment_status='paid'"); paid_invoices = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) AS c FROM invoices WHERE payment_status='unpaid'"); unpaid_invoices = cur.fetchone()["c"]

        cur.execute("SELECT SUM(total_amt) AS r FROM invoices WHERE payment_status='paid'")
        revenue = cur.fetchone()["r"] or 0

        cur.execute("SELECT name, quantity FROM parts ORDER BY name")
        inventory = cur.fetchall()

        conn.close()

        # ---- Format Report ----
        report = []
        report.append("=========== CAR SERVICE CENTER - GENERAL REPORT ===========")
        report.append(f"Generated On: {datetime.datetime.now()}\n")

        report.append("--------------- SUMMARY ---------------")
        report.append(f"Total Customers         : {total_customers}")
        report.append(f"Total Vehicles          : {total_vehicles}\n")

        report.append("--------------- JOB CARDS ---------------")
        report.append(f"Total Jobs Created      : {total_jobs}")
        report.append(f"Pending Jobs            : {pending_jobs}")
        report.append(f"Completed Jobs          : {completed_jobs}\n")

        report.append("--------------- INVOICES ---------------")
        report.append(f"Total Invoices          : {total_invoices}")
        report.append(f"Paid Invoices           : {paid_invoices}")
        report.append(f"Unpaid Invoices         : {unpaid_invoices}")
        report.append(f"Total Revenue (Paid)    : ₹{revenue}\n")

        report.append("--------------- INVENTORY SUMMARY ---------------")
        for item in inventory:
            report.append(f" - {item['name']} : {item['quantity']} units")

        report.append("\n===========================================================\n")

        # Display in text box
        self.report_box.config(state="normal")
        self.report_box.delete("1.0", tk.END)
        self.report_box.insert(tk.END, "\n".join(report))
        self.report_box.config(state="disabled")  # lock editing

