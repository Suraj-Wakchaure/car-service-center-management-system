import tkinter as tk
from tkinter import ttk, messagebox
from database.database import get_conn

class VehiclesPage(tk.Frame):
    def __init__(self, root, role):
        super().__init__(root, bg="#FFFFFF")
        self.role = role

        # UI style
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 10))

        ttk.Label(self, text="Vehicles", font=("Segoe UI", 14, "bold")).pack(pady=10)

        columns = ("id", "customer_name", "reg_no", "model", "year", "distance_traveled")
        self.tree_table = ttk.Treeview(self, columns=columns, show="headings", height=15)

        for col in columns:
            self.tree_table.heading(col, text=col.replace("_", " ").title())
            self.tree_table.column(col, width=120)

        self.tree_table.pack(padx=10, pady=10, fill="both", expand=True)

        # Buttons Frame
        btn_frame = tk.Frame(self, bg="#FFFFFF")
        btn_frame.pack(pady=(4, 20))

        # Receptionist CAN add vehicles
        ttk.Button(btn_frame, text="Add Vehicle", command=self.add_vehicle).grid(row=0, column=0, padx=5)

        # ❌ Receptionist CANNOT delete vehicles
        if self.role == "admin":
            ttk.Button(btn_frame, text="Delete Vehicle", command=self.delete_vehicle).grid(row=0, column=1, padx=5)

        ttk.Button(btn_frame, text="Refresh", command=self.refresh).grid(row=0, column=2, padx=5)

        self.refresh()

    def refresh(self):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT v.id, c.name AS customer_name, v.reg_no, v.model, v.year, v.distance_traveled
            FROM vehicles v
            JOIN customers c ON v.customer_id = c.id
            ORDER BY v.id DESC
        """)
        rows = cur.fetchall()
        conn.close()

        self.tree_table.delete(*self.tree_table.get_children())

        for row in rows:
            self.tree_table.insert(
                "", "end",
                values=(row["id"], row["customer_name"], row["reg_no"],
                        row["model"], row["year"], row["distance_traveled"])
            )

    def add_vehicle(self):
        add_window = tk.Toplevel(self)
        add_window.title("Add Vehicle")
        add_window.geometry("400x350")
        add_window.grab_set()

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM customers")
        customers = cur.fetchall()
        conn.close()

        ttk.Label(add_window, text="Customer:").grid(row=0, column=0, padx=10, pady=8, sticky="w")

        cust_var = tk.StringVar()
        customer_dropdown = ttk.Combobox(add_window, textvariable=cust_var,
                                         values=[f"{c['id']} - {c['name']}" for c in customers], width=25)
        customer_dropdown.grid(row=0, column=1, padx=10, pady=8)

        fields = ["Reg No", "Model", "Year", "Distance traveled"]
        entries = {}

        for i, label in enumerate(fields, start=1):
            ttk.Label(add_window, text=label + ":").grid(row=i, column=0, padx=10, pady=8, sticky="w")
            entries[label] = ttk.Entry(add_window, width=25)
            entries[label].grid(row=i, column=1, padx=10, pady=8)

        def save_vehicle():
            if not cust_var.get():
                messagebox.showwarning("Missing Info", "Please select a customer.")
                return

            cust_id = cust_var.get().split(" - ")[0]

            reg_no = entries["Reg No"].get().strip()
            model = entries["Model"].get().strip()
            year = entries["Year"].get().strip()
            distance_traveled = entries["Distance traveled"].get().strip()

            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO vehicles (customer_id, reg_no, model, year, distance_traveled)
                VALUES (?, ?, ?, ?, ?)
            """, (cust_id, reg_no, model, year, distance_traveled))

            conn.commit()
            conn.close()
            add_window.destroy()
            self.refresh()
            messagebox.showinfo("Success", "Vehicle added successfully!")

        ttk.Button(add_window, text="Save", command=save_vehicle).grid(row=6, column=1, pady=15)

    def delete_vehicle(self):
        selected = self.tree_table.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a vehicle.")
            return

        vehicle_id = self.tree_table.item(selected[0])["values"][0]

        if messagebox.askyesno("Confirm", "Are you sure to delete this vehicle?"):
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("DELETE FROM vehicles WHERE id=?", (vehicle_id,))
            conn.commit()
            conn.close()
            self.refresh()
            messagebox.showinfo("Deleted", "Vehicle deleted successfully.")
