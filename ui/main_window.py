import tkinter as tk
from tkinter import ttk, messagebox
from ui.customers_page import CustomersPage
from ui.vehicles_page import VehiclesPage
from ui.parts_page import PartsPage
from ui.job_cards_page import JobCardsPage
from ui.invoices_page import InvoicesPage
from ui.reports_page import ReportsPage
from models.theme import *
def open_main_window(user, parent_window):

    window = tk.Toplevel(parent_window)

    window.title("Car Service Center - Dashboard")
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window.geometry(f"{screen_width}x{screen_height}")
    window.configure(bg=HEADER_BG)
    style = ttk.Style()
    
    style.theme_use("clam")
    style.configure("TButton", font=LABLE_FONT, borderwidth=1)
    
    header_frame = tk.Frame(window, bg=HEADER_BG, height=50)
    header_frame.pack(side="top", fill="both", pady=10)

    tk.Label(header_frame, text="Car Service Center Management System", fg=LABLE_BG, bg=HEADER_BG, font=("Segoe UI", 15)).pack(side="left", padx=20)

    tk.Label(
        header_frame,
        text=f"Logged in as {user['fullname']} ({user['role']})",
        bg=HEADER_BG, fg="#C75A1A", font=("Segoe UI", 14)
    ).pack(side="right", padx=15)

    role = user["role"]

    sidebar = tk.Frame(window, bg=MENU_FRAME_BG, width=300)
    sidebar.pack(side="left", fill="y")

    content_frame = tk.Frame(window, bg=CONTENT_BG)
    content_frame.pack(side="right", fill="both", expand=True)

    def show_frame(page):
        for widget in content_frame.winfo_children():
            widget.destroy()
        frame = page(content_frame, role)
        frame.pack(fill="both", expand=True)

    # Role-based buttons
    buttons = []

    # Admin full access
    if role == "admin":
        buttons = [
            ("Customers", lambda: show_frame(CustomersPage)),
            ("Vehicles", lambda: show_frame(VehiclesPage)),
            ("Parts", lambda: show_frame(PartsPage)),
            ("Job Cards", lambda: show_frame(JobCardsPage)),
            ("Invoices", lambda: show_frame(InvoicesPage)),
            ("Reports", lambda: show_frame(ReportsPage))
        ]

    # Receptionist restricted access
    elif role == "receptionist":
        buttons = [
            ("Customers", lambda: show_frame(CustomersPage)),
            ("Vehicles", lambda: show_frame(VehiclesPage)),
            ("Parts", lambda: show_frame(PartsPage)),
            ("Job Cards", lambda: show_frame(JobCardsPage)),
            ("Invoices", lambda: show_frame(InvoicesPage)),
        ]

    def on_close():
        parent_window.destroy()
        window.destroy()

    buttons.append(("Logout", on_close))

    for name, cmd in buttons:
        ttk.Button(sidebar, text=name, command=cmd, width=20).pack(padx=10, pady=10)

    tk.Label(
        content_frame,
        text="Welcome to Car Service Center Dashboard",
        bg="#FFFFFF",
        font=("Segoe UI", 15, "bold")
    ).pack(pady=200)

    window.protocol("WM_DELETE_WINDOW", on_close)
    window.mainloop()
