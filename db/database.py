import sqlite3
import os

def connexion_db():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path  = os.path.join(base_dir, "data", "paysagisme.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn