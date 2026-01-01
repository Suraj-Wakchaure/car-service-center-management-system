import tkinter as tk
from tkinter import ttk, messagebox
from database.database import get_conn

class JobCardsPage(tk.Frame):
    def __init__(self, root, role):
        super().__init__(root, bg="#FFFFFF")
        self.role = role

        #UI style
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 10))

        ttk.Label(self, text="Job Cards", font=("Segoe UI", 14, "bold")).pack(pady=10)

        columns = ("id", "job_no", "customer_name", "vehicle_reg", "description", "labour_charges", "status", "created_at")
        self.tree_table = ttk.Treeview(self, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree_table.heading(col, text=col.replace("_", " ").title())
            self.tree_table.column(col, width=130)
        self.tree_table.pack(padx=10, pady=10, fill="both", expand=True)

        # Buttons
        btn_frame = tk.Frame(self, bg="#FFFFFF")
        btn_frame.pack(pady=(4, 20))
        ttk.Button(btn_frame, text="Add Job", command=self.add_job).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Assign Parts", command=self.assign_parts).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Mark Completed", command=self.mark_completed).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.refresh).grid(row=0, column=3, padx=5)
        ttk.Button(btn_frame, text="Print Job Card", command=self.printJobcard).grid(row=0, column=4, padx=5)
        self.refresh()

    def refresh(self):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT j.id, j.job_no, c.name AS customer_name, v.reg_no AS vehicle_reg, j.description, j.labour_charges, j.status, j.created_at
            FROM job_cards j
            JOIN vehicles v ON j.vehicle_id = v.id
            JOIN customers c ON v.customer_id = c.id
            ORDER BY j.id DESC
        """)
        rows = cur.fetchall()
        conn.close()

        self.tree_table.delete(*self.tree_table.get_children())
        for row in rows:
            self.tree_table.insert("", "end", values=(row["id"], row["job_no"], row["customer_name"], row["vehicle_reg"], row["description"], row["labour_charges"], row["status"], row["created_at"]))

    def add_job(self):
        add_window = tk.Toplevel(self)
        add_window.title("Add Job Card")
        add_window.geometry("400x400")
        add_window.grab_set()

        # Vehicle Dropdown
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, reg_no FROM vehicles")
        vehicles = cur.fetchall()
        conn.close()

        ttk.Label(add_window, text="Vehicle:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        vehicle_var = tk.StringVar()
        vehicle_dropdown = ttk.Combobox(add_window, textvariable=vehicle_var, values=[f"{v['id']} - {v['reg_no']}" for v in vehicles], width=25)
        vehicle_dropdown.grid(row=0, column=1, padx=10, pady=8)

        ttk.Label(add_window, text="Description:").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        desc_entry = ttk.Entry(add_window, width=30)
        desc_entry.grid(row=1, column=1, padx=10, pady=8)

        ttk.Label(add_window, text="Labour Charges:").grid(row=2, column=0, padx=10, pady=8, sticky="w")
        labour_entry = ttk.Entry(add_window, width=30)
        labour_entry.grid(row=2, column=1, padx=10, pady=8)

        def save_job():
            if not vehicle_var.get():
                messagebox.showwarning("Missing", "Select a vehicle first!")
                return

            vehicle_id = vehicle_var.get().split(" - ")[0]
            desc = desc_entry.get().strip()
            labour = float(labour_entry.get().strip() or 0)

            job_no = f"JOB{vehicle_id}{int(labour*10)}"  # simple auto job number

            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO job_cards (job_no, vehicle_id, description, labour_charges)
                VALUES (?, ?, ?, ?)
            """, (job_no, vehicle_id, desc, labour))
            conn.commit()
            conn.close()

            add_window.destroy()
            self.refresh()
            messagebox.showinfo("Success", "Job added successfully!")

        ttk.Button(add_window, text="Save", command=save_job).grid(row=4, column=1, pady=15)
        


    def assign_parts(self):
        selected = self.tree_table.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a job first.")
            return

        job_id = self.tree_table.item(selected[0])["values"][0]

        assign_window = tk.Toplevel(self)
        assign_window.title("Assign Parts to Job")
        assign_window.geometry("400x350")
        assign_window.grab_set()

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, name, quantity, unit_price FROM parts WHERE quantity > 0")
        parts = cur.fetchall()
        conn.close()

        ttk.Label(assign_window, text="Part:").grid(row=0, column=0, padx=10, pady=8)
        part_var = tk.StringVar()

        # Dropdown with ID - Name (Qty)
        part_dropdown = ttk.Combobox(assign_window,
        textvariable=part_var, values=[f"{p['id']} - {p['name']} ({p['quantity']})" for p in parts], width=30)
        part_dropdown.grid(row=0, column=1, padx=10, pady=8)

        ttk.Label(assign_window, text="Quantity:").grid(row=1, column=0, padx=10, pady=8)
        qty_entry = ttk.Entry(assign_window, width=25)
        qty_entry.grid(row=1, column=1, padx=10, pady=8)

        ttk.Label(assign_window, text="Price per Unit:").grid(row=2, column=0, padx=10, pady=8)

        price_var = tk.StringVar()
        price_entry = ttk.Entry(assign_window, textvariable=price_var, width=25, state="readonly")
        price_entry.grid(row=2, column=1, padx=10, pady=8)

        # Auto-fill unit price when part is selected
        def fill_price(event):
            selected_text = part_var.get()
            if not selected_text:
                return
        
            part_id = selected_text.split(" - ")[0]

            for p in parts:
                if str(p["id"]) == part_id:
                    price_var.set(p["unit_price"])
                    break

        part_dropdown.bind("<<ComboboxSelected>>", fill_price)

        def save_assignment():
            if not part_var.get():
                messagebox.showwarning("Select", "Please select a part.")
                return

            part_id = part_var.get().split(" - ")[0]
            qty = int(qty_entry.get().strip() or 0)
            price = float(price_var.get().strip() or 0)

            conn = get_conn()
            cur = conn.cursor()

            # check stock
            cur.execute("SELECT quantity FROM parts WHERE id=?", (part_id,))
            stock = cur.fetchone()["quantity"]

            if qty > stock:
                messagebox.showerror("Error", f"Not enough stock! Available: {stock}")
                conn.close()
                return

            # Deduct stock
            cur.execute("UPDATE parts SET quantity = quantity - ? WHERE id=?", (qty, part_id))

            # Insert job_parts
            cur.execute("""
                INSERT INTO job_parts (job_id, part_id, qty, price)
                VALUES (?, ?, ?, ?)
            """, (job_id, part_id, qty, price))

            conn.commit()
            conn.close()
            assign_window.destroy()
            messagebox.showinfo("Assigned", "Parts assigned and stock updated.")

        ttk.Button(assign_window, text="Save", command=save_assignment).grid(row=4, column=1, pady=15)

    def mark_completed(self):
        selected = self.tree_table.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a job to mark as completed.")
            return

        job_id = self.tree_table.item(selected[0])["values"][0]

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE job_cards SET status='completed' WHERE id=?", (job_id,))
        conn.commit()

        # Generate invoice
        cur.execute("""
            SELECT SUM(qty * price) AS total_parts, labour_charges, vehicle_id
            FROM job_cards 
            JOIN job_parts ON job_cards.id = job_parts.job_id
            WHERE job_cards.id=?
        """, (job_id,))
        data = cur.fetchone()

        total_parts = data["total_parts"] or 0
        labour = data["labour_charges"] or 0
        total = total_parts + labour

        # Find customer
        cur.execute("SELECT c.id FROM customers c JOIN vehicles v ON v.customer_id=c.id WHERE v.id=?",
                    (data["vehicle_id"],))
        cust = cur.fetchone()
        cust_id = cust["id"] if cust else None

        invoice_no = f"INV{job_id}{int(total)}"

        cur.execute("""
            INSERT INTO invoices (job_id, invoice_no, billed_to_customer_id,
                                  total_parts_cost, labour_charges, total_amt)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (job_id, invoice_no, cust_id, total_parts, labour, total))
        conn.commit()
        conn.close()
        
    def printJobcard(self):
        selected = self.tree_table.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a Job card.")
            return

        values = self.tree_table.item(selected[0])["values"]

        job_id      = values[0]
        job_no      = values[1]
        customer_name = values[2]
        vehicle_reg = values[3]
        desc        = values[4]
        labour      = values[5]
        status      = values[6]
        created_at  = values[7]

        # Fetch extra data
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            SELECT v.model, v.year, c.name AS customer_name, c.phone 
            FROM vehicles v 
            JOIN customers c ON v.customer_id = c.id 
            WHERE v.reg_no = ?
        """, (vehicle_reg,))
        vehicle_data = cur.fetchone()

        model = vehicle_data["model"] if vehicle_data else "N/A"
        year = vehicle_data["year"] if vehicle_data else "N/A"
        cust_phone = vehicle_data["phone"] if vehicle_data else "N/A"

        cur.execute("""
            SELECT p.name, jp.qty
            FROM job_parts jp
            JOIN parts p ON p.id = jp.part_id
            WHERE jp.job_id = ?
        """, (job_id,))
        parts = cur.fetchall()

        conn.close()

        safe_cust_name = customer_name.replace(" ", "_")
        filename = f"JobCard_{job_no}_{safe_cust_name}.txt"

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("========= CAR SERVICE CENTER JOB CARD =========\n\n")
                f.write(f"Job No           : {job_no}\n")
                f.write(f"Customer Name    : {customer_name}\n")
                f.write(f"Vehicle Reg. No  : {vehicle_reg}\n")
                f.write(f"Vehicle Model    : {model} ({year})\n")
                f.write(f"Contact Number   : {cust_phone}\n")
                f.write(f"Description      : {desc}\n")
                f.write(f"Labour Charges   : ₹{labour}\n")
                f.write(f"Status           : {status}\n")
                f.write(f"Created On       : {created_at}\n")
                f.write("\n-----------------------------------------------\n")
                f.write("Parts Assigned:\n")

                if parts:
                    for p in parts:
                        f.write(f" - {p['name']} (Qty: {p['qty']})\n")
                else:
                    f.write("No parts assigned yet.\n")

                f.write("\n-----------------------------------------------\n")
                f.write("Mechanic Instructions:\n")
                f.write(" - Verify all assigned parts.\n")
                f.write(" - Perform service as per description.\n")
                f.write("\n===============================================\n")

            messagebox.showinfo("Saved", f"Job Card saved as {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Could not save Job Card: {e}")

        self.refresh()
