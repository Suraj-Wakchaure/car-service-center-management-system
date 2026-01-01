import tkinter as tk
from tkinter import ttk, messagebox
from database.database import get_conn

class PartsPage(tk.Frame):
    def __init__(self, root, role):
        super().__init__(root, bg="#FFFFFF")
        self.role = role

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 10))

        ttk.Label(self, text="Parts Inventory", font=("Segoe UI", 14, "bold")).pack(pady=10)

        columns = ("id", "part_code", "name", "quantity", "unit_price", "supplier")
        self.tree_table = ttk.Treeview(self, columns=columns, show="headings", height=15)

        for col in columns:
            self.tree_table.heading(col, text=col.replace("_", " ").title())
            self.tree_table.column(col, width=120)

        self.tree_table.pack(padx=10, pady=10, fill="both", expand=True)

        btn_frame = tk.Frame(self, bg="#FFFFFF")
        btn_frame.pack(pady=(4, 20))

 
        if self.role == "admin":
            ttk.Button(btn_frame, text="Add / Restock Part", command=self.add_part).grid(row=0, column=0, padx=5)
            ttk.Button(btn_frame, text="Delete Part", command=self.delete_part).grid(row=0, column=1, padx=5)

        ttk.Button(btn_frame, text="Refresh", command=self.refresh).grid(row=0, column=2, padx=5)

        self.refresh()

    def refresh(self):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM parts ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()

        self.tree_table.delete(*self.tree_table.get_children())
        for row in rows:
            self.tree_table.insert("", "end", values=tuple(row))

    def add_part(self):
        window = tk.Toplevel(self)
        window.title("Add / Restock Part")
        window.geometry("350x350")
        window.grab_set()

        labels = ["Part Code", "Name", "Quantity", "Unit Price", "Supplier"]
        entries = {}

        for i, label in enumerate(labels):
            ttk.Label(window, text=f"{label}:").grid(row=i, column=0, padx=10, pady=8)
            entries[label] = ttk.Entry(window, width=25)
            entries[label].grid(row=i, column=1, padx=10)

        def save():
            code = entries["Part Code"].get().strip()
            name = entries["Name"].get().strip()
            qty = entries["Quantity"].get().strip()
            price = entries["Unit Price"].get().strip()
            supplier = entries["Supplier"].get().strip()

            if name == "":
                messagebox.showwarning("Missing", "Part name required")
                return

            conn = get_conn()
            cur = conn.cursor()
            cur.execute("SELECT * FROM parts WHERE part_code=?", (code,))
            existing = cur.fetchone()

            if existing:
                cur.execute(
                    "UPDATE parts SET quantity=quantity+?, unit_price=?, supplier=? WHERE part_code=?",
                    (qty, price, supplier, code)
                )
            else:
                cur.execute(
                    "INSERT INTO parts(part_code,name,quantity,unit_price,supplier) VALUES (?,?,?,?,?)",
                    (code, name, qty, price, supplier)
                )

            conn.commit()
            conn.close()
            window.destroy()
            self.refresh()
            messagebox.showinfo("Success", "Part saved.")

        ttk.Button(window, text="Save", command=save).grid(row=6, column=1, pady=15)

    def delete_part(self):
        selected = self.tree_table.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a part")
            return

        part_id = self.tree_table.item(selected[0])["values"][0]

        if not messagebox.askyesno("Confirm", "Delete this part?"):
            return

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM parts WHERE id=?", (part_id,))
        conn.commit()
        conn.close()

        self.refresh()
        messagebox.showinfo("Deleted", "Part deleted.")
