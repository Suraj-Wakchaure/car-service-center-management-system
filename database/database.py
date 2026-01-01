import sqlite3
import hashlib

DB_NAME = "database/car_service.db"

def get_conn():
    #connet to the Database
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def DBSchema():
    conn = get_conn()
    cur = conn.cursor()

    #create tables
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS user(
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        fullname TEXT,
        role TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP            
    );

    CREATE TABLE IF NOT EXISTS customers(
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT,
        address TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );                  
                      
    CREATE TABLE IF NOT EXISTS vehicles(
        id INTEGER PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        reg_no TEXT UNIQUE NOT NULL,
        model TEXT,
        year INTEGER,
        distance_traveled INTEGER,
        FOREIGN KEY(customer_id) REFERENCES customers(id)                  
    );
                      
    CREATE TABLE IF NOT EXISTS parts(
        id INTEGER PRIMARY KEY,
        part_code TEXT UNIQUE,
        name TEXT NOT NULL,
        quantity INTEGER DEFAULT 0,
        unit_price REAL DEFAULT 0.0,
        supplier TEXT
    );
                      
    CREATE TABLE IF NOT EXISTS job_cards(
        id INTEGER PRIMARY KEY,
        part_code TEXT UNIQUE,
        job_no TEXT UNIQUE,
        vehicle_id INTEGER NOT NULL,
        description TEXT,
        labour_charges REAL DEFAULT 0.0,
        status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(vehicle_id) REFERENCES vehicles(id)                     
    );
                      
    CREATE TABLE IF NOT EXISTS job_parts(
        id INTEGER PRIMARY KEY,
        job_id INTEGER,
        part_id INTEGER,
        qty INTEGER,
        price REAL,
        FOREIGN KEY(job_id) REFERENCES job_cards(id),
        FOREIGN KEY(part_id) REFERENCES  parts(id)
    );

    CREATE TABLE IF NOT EXISTS invoices(
        id INTEGER PRIMARY KEY,
        job_id INTEGER UNIQUE,
        invoice_no TEXT UNIQUE,
        billed_to_customer_id INTEGER,
        total_parts_cost REAL,
        labour_charges REAL,
        total_amt REAL,
        payment_status TEXT DEFAULT 'unpaid',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(job_id) REFERENCES job_cards(id),
        FOREIGN KEY(billed_to_customer_id) REFERENCES customers(id)
    );
    """)
    
    #seeding admin user
    cur.execute("SELECT * FROM user WHERE role = 'admin'")
    if cur.fetchone() is None:
        encoded_password = "admin2004".encode()

        #create hash object
        hash_obj = hashlib.sha256(encoded_password)
        #convert to hexadecimal representation
        hashed_pass = hash_obj.hexdigest()
        cur.execute(
            "INSERT INTO user(username, hashed_password, fullname, role) VALUES(?,?,?,?)", ("admin", hashed_pass, "Administrator", "admin")
        )

        print("✅ Admin user created [username = 'admin' password = 'admin2004']")
    
    print("Seeding sample data...")

    #Insert customers
    cur.execute("SELECT COUNT(*) FROM customers")
    if cur.fetchone()[0] == 0:
        customers = [
            ("Suraj Wakchaure", "9876543210", "suraj@gmail.com", "Talegaon Dabhade"),
            ("Swapnil Sawant", "9856421133", "sawantswap@gmail.seth", "Sawant niwas, Shinde Wasti, Somatne Phata"),
            ("Sumit Kate", "9871254789", "kate@mail.kar", "Yewla, Nashik"),
            ("Shubham Sathe", "9823456790", "donmhantat@gmail.com", "Parner, Ahilyanagar"),
            ("Agasti Kahar", "9876504321", "nadkaraychanay@kahar.com", "Dholakpur, Nepal")
        ]
        cur.executemany(
            "INSERT INTO customers(name, phone, email, address) VALUES(?, ?, ?, ?)", customers
        )
        print("✅ Customers added")

    #Insert vehicles
    cur.execute("SELECT COUNT(*) FROM vehicles")
    if cur.fetchone()[0] == 0:
        vehicles = [
            (1, "MH12AB1234", "Swift Desire", 2020, 15000),
            (2, "MH14CD5678", "WagonR", 2019, 22000),
            (3, "MH15EF9988", "Creta", 2021, 10000),
            (4, "MH20GH7654", "Baleno", 2018, 30000),
            (5, "MH31JK1122", "i20 Sportz", 2022, 8000)
        ]
        cur.executemany(
            "INSERT INTO vehicles(customer_id, reg_no, model, year, distance_traveled) VALUES(?, ?, ?, ?, ?)",
            vehicles
        )
        print("✅ Vehicles added")

    #Insert parts
    cur.execute("SELECT COUNT(*) FROM parts")
    if cur.fetchone()[0] == 0:
        parts = [
            ("P001", "Engine Oil", 50, 550.00, "Castrol"),
            ("P002", "Air Filter", 25, 350.00, "Bosch"),
            ("P003", "Brake Pad", 40, 800.00, "TVS"),
            ("P004", "Coolant", 30, 600.00, "Shell"),
            ("P005", "Wiper Blade", 20, 250.00, "3M"),
            ("P006", "Spark Plug", 60, 120.00, "NGK"),
            ("P007", "Clutch Plate", 15, 1500.00, "Valeo"),
            ("P008", "Battery 12V", 10, 4800.00, "Exide"),
            ("P009", "Tyre 175/65R14", 8, 4200.00, "MRF"),
            ("P010", "Fuel Pump", 5, 3200.00, "Delphi")
        ]
        cur.executemany(
            "INSERT INTO parts(part_code, name, quantity, unit_price, supplier) VALUES(?, ?, ?, ?, ?)",
            parts
        )
        print("✅ Parts added")

    

    # Seeding receptionist user
    cur.execute("SELECT * FROM user WHERE role = 'receptionist'")
    if cur.fetchone() is None:
        encoded_password = "reception@2004".encode()
        hash_obj = hashlib.sha256(encoded_password)
        hashed_pass = hash_obj.hexdigest()

        cur.execute("INSERT INTO user(username, hashed_password, fullname, role) VALUES(?,?,?,?)",
            ("receptionist", hashed_pass, "Front Desk Receptionist", "receptionist"))

        print("✅ Receptionist user created [username='receptionist' password='reception@2004']")

    cur.execute("SELECT * FROM user WHERE role = 'receptionist'")
    if cur.fetchone():
        encoded_password = "recep".encode()
        hash_obj = hashlib.sha256(encoded_password)
        hashed_pass = hash_obj.hexdigest()

        cur.execute("UPDATE user SET hashed_password = ? WHERE role = 'receptionist'", (hashed_pass,))
        print("✅ Password for receptionist changed successfully!")

    conn.commit()
    print("🌱 Database seeding complete.")
    conn.close()
    
#run this file directly once to create the databse
if __name__ == "__main__":
    DBSchema()