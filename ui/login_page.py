import tkinter as tk
from tkinter import ttk, messagebox
from models.user_model import authenticate
from ui.main_window import open_main_window
from models.theme import *
def open_login_page():
    window = tk.Tk()

    window.title("Car Service Center - Login")
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width / 2) - (300 / 2))
    y = int((screen_height / 2) - (250 / 2))
    window.geometry(f"{300}x{250}+{x}+{y}")
    window.configure(bg=LABLE_BG)

    #UI style
    style = ttk.Style()
    
    style.theme_use("clam")
    
    
    window.columnconfigure(2, weight = 2)
    window.rowconfigure(2, weight = 2)

    ttk.Label(window, text="Login", font=("Segoe UI", 17, "bold"), background=LABLE_BG, foreground=LABEL_FG).pack(pady=14)
    
    frame = ttk.Frame(window)
    style.configure("TFrame", background=LABLE_BG)
    frame.pack()

    style.configure("TLabel", foreground=LABEL_FG, font=LABLE_FONT)
    style.configure("TButton", font=LABLE_FONT, borderwidth=1)
    style.configure("TEntry", font=LABLE_FONT, borderwidth = 0, padding=2)
    #take username and password
    ttk.Label(frame, text="Username", background=LABLE_BG).grid(row=0,column=0, padx=10, pady=10)
    username_var = tk.StringVar()
    ttk.Entry(frame, textvariable=username_var, width=25).grid(row=0, column = 1, padx=10, pady=10)

    ttk.Label(frame, text="Password", background=LABLE_BG).grid(row=1,column=0, padx=10, pady=10)
    password_var = tk.StringVar()
    ttk.Entry(frame, textvariable=password_var, width=25, show="•").grid(row=1, column = 1, padx=10, pady=10)

    #login button action
    def handle_login():
        username = username_var.get().strip()
        password = password_var.get().strip()

        if username=="" or password=="":
            messagebox.showwarning("Missing Info", "Enter both username and password.")
            return
        user = authenticate(username, password)#this returns a dictionary of user row or tuple
        if user:
            messagebox.showinfo("Succees", f"Welcome {user['fullname']} ({user['role']})")
            window.withdraw()
            open_main_window(user, window) #pass user information to the main window
        else:
            messagebox.showerror("Error", "Invalid username or password")
    
    #button widget
    ttk.Button(frame, text="Login", command=handle_login).grid(row=2, column=0, columnspan=2, padx=10, pady=15)




    window.mainloop()

if __name__ == "__main__":
    open_login_page()