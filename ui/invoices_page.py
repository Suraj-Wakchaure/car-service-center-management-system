import tkinter as tk
from tkinter import ttk, messagebox
from database.database import get_conn
from models.theme import *

class InvoicesPage(tk.Frame):
    def __init__(self, root, role):
        super().__init__(root, bg="#FFFFFF")
        self.role = role
        # UI style
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 10))
        style.configure("TLabel", foreground=LABEL_FG, background=LABLE_BG)
        
        ttk.Label(self, text="Invoices", font=TABLE_NAME_FONT).pack(pady=10)

        # Added customer_name column
        columns = (
            "id", "invoice_no", "job_id", "customer_name",
            "total_parts_cost", "labour_charges", "total_amt", "payment_status"
        )

        self.tree_table = ttk.Treeview(self, columns=columns, show="headings", height=15)

        for col in columns:
            self.tree_table.heading(col, text=col.replace("_", " ").title())
            self.tree_table.column(col, width=130)

        self.tree_table.pack(padx=10, pady=10, fill="both", expand=True)

        ttk.Button(self, text="Export Invoice", command=self.printInvoice).pack()
        ttk.Button(self, text="Mark as Paid", command=self.mark_paid).pack(pady=(4,20))

        self.refresh()

    def refresh(self):
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                i.id, 
                i.invoice_no, 
                i.job_id, 
                c.name AS customer_name,
                i.total_parts_cost, 
                i.labour_charges, 
                i.total_amt, 
                i.payment_status
            FROM invoices i
            JOIN customers c ON i.billed_to_customer_id = c.id
            ORDER BY i.id DESC
        """)

        rows = cur.fetchall()
        conn.close()

        self.tree_table.delete(*self.tree_table.get_children())

        for row in rows:
            self.tree_table.insert(
                "", "end",
                values=(
                    row["id"], row["invoice_no"], row["job_id"],
                    row["customer_name"], row["total_parts_cost"],
                    row["labour_charges"], row["total_amt"], row["payment_status"]
                )
            )


    def printInvoice(self):
        selected = self.tree_table.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select an invoice.")
            return

        values = self.tree_table.item(selected[0])["values"]

        inv_no        = values[1]
        job_id        = values[2]
        cust_name     = values[3]
        parts_cost    = values[4]
        labour        = values[5]
        total         = values[6]
        status        = values[7]

        # Make safe filename
        safe_name = cust_name.replace(" ", "_")
        filename = f"Invoice_{inv_no}_{safe_name}.txt"

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("====== Car Service Center Invoice ======\n\n")
                f.write(f"Invoice No     : {inv_no}\n")
                f.write(f"Job ID         : {job_id}\n")
                f.write(f"Customer Name  : {cust_name}\n")
                f.write(f"Total Parts    : ₹{parts_cost}\n")
                f.write(f"Labour Charges : ₹{labour}\n")
                f.write(f"Total Amount   : ₹{total}\n")
                f.write(f"Payment Status : {status}\n")
                f.write("\n----------------------------------------\n")
                f.write("Thank you for choosing Car Service Center!\n")

            messagebox.showinfo("Exported", f"Invoice saved as {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Could not save invoice: {e}")

    def mark_paid(self):
        selected = self.tree_table.selection()
        if not selected:
            messagebox.showwarning("Select", "Select an invoice to mark as paid.")
            return

        inv_id = self.tree_table.item(selected[0])["values"][0]

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE invoices SET payment_status='paid' WHERE id=?", (inv_id,))
        conn.commit()
        conn.close()

        self.refresh()
        messagebox.showinfo("Updated", "Payment marked as paid.")