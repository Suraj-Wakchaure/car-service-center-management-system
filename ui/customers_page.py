import tkinter as tk
from tkinter import ttk, messagebox
from database.database import get_conn
from models.theme import *
class CustomersPage(tk.Frame):
    def __init__(self, root, role):
        super().__init__(root, bg="#FFFFFF")
        self.role = role

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 10))
        style.configure("TLabel", foreground=LABEL_FG, background=LABLE_BG)
        
        ttk.Label(self, text="Customers", font=TABLE_NAME_FONT).pack(pady=10)
        
        columns = ("id", "name", "phone", "email", "address")
        self.tree_table = ttk.Treeview(self, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree_table.heading(col, text=col.capitalize())
            self.tree_table.column(col, width=150)

        # Search bar
        search_frame = tk.Frame(self, bg="#FFFFFF")
        search_frame.pack(pady=5)

        tk.Label(search_frame, text="Search by Name or Phone: ", bg="#FFFFFF").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var, width=25).pack(side="left", padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_customer).pack(side="left", padx=5)
        ttk.Button(search_frame, text="Clear", command=self.refresh).pack(side="left", padx=5)

        self.tree_table.pack(padx=10, pady=10, fill="both", expand=True)

        # Buttons
        btn_frame = tk.Frame(self, bg="#FFFFFF")
        btn_frame.pack(pady=(4, 20))

        ttk.Button(btn_frame, text="Add Customer", command=self.add_customer).grid(row=0, column=0, padx=5)


        if self.role == "admin":
            ttk.Button(btn_frame, text="Delete Customer", command=self.delete_customer).grid(row=0, column=1, padx=5)

        ttk.Button(btn_frame, text="Refresh", command=self.refresh).grid(row=0, column=2, padx=5)

        self.refresh()

    def search_customer(self):
        keyword = self.search_var.get().strip()
        if keyword == "":
            self.refresh()
            return

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM customers
            WHERE name LIKE ? OR phone LIKE ?
            ORDER BY id DESC
        """, (f"%{keyword}%", f"%{keyword}%"))
        rows = cur.fetchall()
        conn.close()

        self.tree_table.delete(*self.tree_table.get_children())
        for row in rows:
            self.tree_table.insert("", "end", values=tuple(row))

    def refresh(self):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM customers ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()

        self.tree_table.delete(*self.tree_table.get_children())
        for row in rows:
            self.tree_table.insert("", "end", values=tuple(row))

    def add_customer(self):
        window = tk.Toplevel(self)
        window.title("Add Customer")
        window.geometry("350x300")
        window.grab_set()

        labels = ["Name", "Phone", "Email", "Address"]
        entries = {}

        for i, label in enumerate(labels):
            ttk.Label(window, text=f"{label}:").grid(row=i, column=0, padx=10, pady=8)
            entries[label] = ttk.Entry(window, width=25)
            entries[label].grid(row=i, column=1, padx=10)

        def save():
            name = entries["Name"].get().strip()
            phone = entries["Phone"].get().strip()
            email = entries["Email"].get().strip()
            address = entries["Address"].get().strip()

            if name == "" or phone == "":
                messagebox.showwarning("Missing", "Name and phone required")
                return

            conn = get_conn()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO customers(name, phone, email, address) VALUES (?, ?, ?, ?)",
                (name, phone, email, address)
            )
            conn.commit()
            conn.close()

            window.destroy()
            self.refresh()
            messagebox.showinfo("Success", "Customer added.")

        ttk.Button(window, text="Save", command=save).grid(row=5, column=1, pady=15)

    def delete_customer(self):
        selected = self.tree_table.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a customer.")
            return

        cust_id = self.tree_table.item(selected[0])["values"][0]

        if not messagebox.askyesno("Confirm", "Delete this customer?"):
            return

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM customers WHERE id=?", (cust_id,))
        conn.commit()
        conn.close()

        self.refresh()
        messagebox.showinfo("Deleted", "Customer deleted.")
