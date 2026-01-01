#handle login and  password verification

from database.database import get_conn
import hashlib

#hash the input password for verification process
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

#verify by matching hashed and the stored password
def verify_pass(password, stored_hash_password):
    return hash_password(password) == stored_hash_password

def authenticate(username, password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE username=?",(username,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        return None
    
    if verify_pass(password, row["hashed_password"]):
        return dict(row)
    
    return None

    