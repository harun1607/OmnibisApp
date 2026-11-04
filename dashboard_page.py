#file Dashboard_page.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame
)
from PyQt6.QtCore import Qt, QTimer
import sqlite3
from datetime import datetime

def create_dashboard_page():
    page = QWidget()
    layout = QVBoxLayout()
    layout.setContentsMargins(30, 30, 30, 30)
    layout.setSpacing(20)

    welcome_label = QLabel("Selamat Datang di Omnibis Dashboard")
    welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1565C0;")
    layout.addWidget(welcome_label, alignment=Qt.AlignmentFlag.AlignTop)

    info_layout = QHBoxLayout()
    info_layout.setSpacing(20)

    penjualan_value_label = QLabel("Rp 0")
    transaksi_value_label = QLabel("0")

    penjualan_frame = create_info_box("Total Penjualan Hari Ini", penjualan_value_label)
    transaksi_frame = create_info_box("Jumlah Transaksi Hari Ini", transaksi_value_label)

    info_layout.addWidget(penjualan_frame)
    info_layout.addWidget(transaksi_frame)
    layout.addLayout(info_layout)

    produk_label = QLabel("📦 Produk Terlaris Hari Ini")
    produk_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin-top: 10px;")
    layout.addWidget(produk_label)

    produk_list_label = QLabel("-")
    produk_list_label.setStyleSheet("""
        font-size: 15px;
        padding: 12px;
        background-color: #f5f5f5;
        border: 1px solid #ddd;
        border-radius: 8px;
        color: #333;
    """)
    layout.addWidget(produk_list_label)

    layout.addStretch()
    page.setLayout(layout)

    last_jumlah_transaksi = {'value': -1}

    def check_and_update_dashboard():
        try:
            conn = sqlite3.connect("OmnibisApp.db")
            cursor = conn.cursor()
            today = datetime.now().strftime("%Y-%m-%d")

            cursor.execute("SELECT COUNT(*) FROM transaksi WHERE tanggal LIKE ?", (today + "%",))
            jumlah_transaksi = cursor.fetchone()[0] or 0

            if jumlah_transaksi != last_jumlah_transaksi['value']:
                last_jumlah_transaksi['value'] = jumlah_transaksi
                update_dashboard_highlights(penjualan_value_label, transaksi_value_label, produk_list_label)

            conn.close()
        except Exception as e:
            print("❌ Gagal cek update dashboard:", e)

    timer = QTimer(page)
    timer.timeout.connect(check_and_update_dashboard)
    timer.start(10000)

    update_dashboard_highlights(penjualan_value_label, transaksi_value_label, produk_list_label)
    last_jumlah_transaksi['value'] = int(transaksi_value_label.text())

    return page


def create_info_box(title, value_widget):
    box = QFrame()
    box.setFrameShape(QFrame.Shape.StyledPanel)
    box.setStyleSheet("""
        QFrame {
            background-color: #1976D2;  /* Warna biru dari logo */
            border-radius: 12px;
            padding: 24px;
        }
    """)

    layout = QVBoxLayout()
    title_label = QLabel(title)
    title_label.setStyleSheet("font-size: 18px; color: white; font-weight: bold;")
    value_widget.setStyleSheet("font-size: 32px; color: white; font-weight: bold;")

    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    value_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

    layout.addWidget(title_label)
    layout.addWidget(value_widget)
    box.setLayout(layout)

    return box


def update_dashboard_highlights(penjualan_label, transaksi_label, produk_list_label):
    try:
        conn = sqlite3.connect("OmnibisApp.db")
        cursor = conn.cursor()

        today = datetime.now().strftime("%Y-%m-%d")

        cursor.execute("""
            SELECT IFNULL(SUM(td.jumlah * p.harga), 0)
            FROM transaksi_detail td
            JOIN transaksi t ON td.id_transaksi = t.id
            JOIN produk p ON td.id_produk = p.id
            WHERE t.tanggal LIKE ?
        """, (today + "%",))
        total_penjualan = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT COUNT(*) FROM transaksi
            WHERE tanggal LIKE ?
        """, (today + "%",))
        jumlah_transaksi = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT p.nama, SUM(td.jumlah) as total_terjual
            FROM transaksi_detail td
            JOIN transaksi t ON td.id_transaksi = t.id
            JOIN produk p ON td.id_produk = p.id
            WHERE t.tanggal LIKE ?
            GROUP BY td.id_produk
            ORDER BY total_terjual DESC
            LIMIT 3
        """, (today + "%",))
        top_produk = cursor.fetchall()

        conn.close()

        penjualan_label.setText(f"Rp {int(total_penjualan):,}".replace(",", "."))
        transaksi_label.setText(str(jumlah_transaksi))

        if top_produk:
            produk_text = "\n".join([f"- {row[0]} ({row[1]}x)" for row in top_produk])
        else:
            produk_text = "- Tidak ada transaksi hari ini"

        produk_list_label.setText(produk_text)

    except Exception as e:
        print("❌ Gagal update dashboard:", e)
