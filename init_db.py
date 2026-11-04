#file init_db.py
import sqlite3

db_OmnibisApp = 'OmnibisApp.db'

def init_db():
    conn = sqlite3.connect(db_OmnibisApp)
    cursor = conn.cursor()

    # Aktifkan foreign key constraints
    cursor.execute('PRAGMA foreign_keys = ON;')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produk (
            id TEXT PRIMARY KEY,
            nama TEXT NOT NULL,
            harga REAL NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT NOT NULL,
            total REAL NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transaksi_detail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_transaksi INTEGER NOT NULL,
            id_produk TEXT NOT NULL,
            jumlah INTEGER NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (id_transaksi) REFERENCES transaksi(id) ON DELETE CASCADE,
            FOREIGN KEY (id_produk) REFERENCES produk(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
    print("Database berhasil dibuat ulang.")
