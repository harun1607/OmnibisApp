#file transaksi_page.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QSpinBox, QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QCompleter, QMessageBox
)
from PyQt6.QtCore import Qt, QStringListModel
from datetime import datetime
import sqlite3


def ambil_barang_dari_db():
    conn = sqlite3.connect("OmnibisApp.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nama, harga FROM produk")
    hasil = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "nama": row[1], "harga": row[2]} for row in hasil]


def parse_rp_to_int(rp_str):
    try:
        angka = rp_str.replace("Rp", "").replace(".", "").replace(",", "").strip()
        if '.' in angka:
            angka = angka.split('.')[0]
        return int(angka)
    except:
        return 0


def update_harga_total(nama_barang, label_harga, label_total, input_jumlah):
    barang_list = ambil_barang_dari_db()
    harga_db = next((b['harga'] for b in barang_list if b['nama'].lower() == nama_barang.lower()), 0)
    harga = int(harga_db)
    label_harga.setText(f"Rp {int(harga):,}".replace(",", "."))
    total = harga * input_jumlah.value()
    label_total.setText(f"Rp {int(total):,}".replace(",", "."))


def update_grand_total(table_transaksi, label_total_all):
    total_semua = 0
    for row in range(table_transaksi.rowCount()):
        item = table_transaksi.item(row, 3)
        if item:
            total = parse_rp_to_int(item.text())
            total_semua += total
    label_total_all.setText(f"Total Keseluruhan: Rp {int(total_semua):,}".replace(",", "."))


def update_total_dan_grand_total(row, table_transaksi, label_total_all):
    try:
        item_jumlah = table_transaksi.item(row, 1)
        item_harga = table_transaksi.item(row, 2)
        if item_jumlah is None or item_harga is None:
            return
        jumlah_item = int(item_jumlah.text())
        harga = parse_rp_to_int(item_harga.text())
        total = jumlah_item * harga
        table_transaksi.blockSignals(True)
        table_transaksi.setItem(row, 3, QTableWidgetItem(f"Rp {total:,}".replace(",", ".")))
        table_transaksi.blockSignals(False)
        update_grand_total(table_transaksi, label_total_all)
    except Exception as e:
        print("Error update total baris:", e)


def tambah_cb(input_nama_barang, input_jumlah, label_harga, table_transaksi, label_total_all):
    nama = input_nama_barang.text().strip()
    if not nama:
        QMessageBox.warning(
            input_nama_barang,                  
            "Peringatan",                       
            "Nama barang tidak boleh kosong."   
        )
        return

    barang_list = ambil_barang_dari_db()
    barang = next((b for b in barang_list if b['nama'].lower() == nama.lower()), None)
    if not barang:
        return

    jumlah = input_jumlah.value()
    harga = int(barang['harga'])
    total = harga * jumlah
    tanggal = datetime.now().strftime("%Y-%m-%d")
    waktu = datetime.now().strftime("%H:%M:%S")

    for row in range(table_transaksi.rowCount()):
        if table_transaksi.item(row, 0) and table_transaksi.item(row, 0).text().lower() == nama.lower():
            current_jumlah = int(table_transaksi.item(row, 1).text())
            new_jumlah = current_jumlah + jumlah
            table_transaksi.setItem(row, 1, QTableWidgetItem(str(new_jumlah)))
            update_total_dan_grand_total(row, table_transaksi, label_total_all)
            return

    row_pos = table_transaksi.rowCount()
    table_transaksi.insertRow(row_pos)
    table_transaksi.setItem(row_pos, 0, QTableWidgetItem(nama))
    table_transaksi.setItem(row_pos, 1, QTableWidgetItem(str(jumlah)))
    table_transaksi.setItem(row_pos, 2, QTableWidgetItem(f"Rp {harga:,}".replace(",", ".")))
    table_transaksi.setItem(row_pos, 3, QTableWidgetItem(f"Rp {total:,}".replace(",", ".")))
    table_transaksi.setItem(row_pos, 4, QTableWidgetItem(tanggal))
    table_transaksi.setItem(row_pos, 5, QTableWidgetItem(waktu))
    update_grand_total(table_transaksi, label_total_all)


def hapus_cb(table_transaksi, label_total_all):
    selected = table_transaksi.currentRow()
    if selected >= 0:
        table_transaksi.removeRow(selected)
        update_grand_total(table_transaksi, label_total_all)


def create_transaksi_page(main_window):
    page = QWidget()
    layout = QVBoxLayout()
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(10)

    form_layout = QHBoxLayout()
    input_nama_barang = QLineEdit()
    input_nama_barang.setPlaceholderText("Ketik nama barang...")

    semua_barang = ambil_barang_dari_db()
    semua_nama = [b['nama'] for b in semua_barang]
    completer_model = QStringListModel(semua_nama)
    completer = QCompleter(completer_model)
    completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
    completer.setFilterMode(Qt.MatchFlag.MatchContains)
    input_nama_barang.setCompleter(completer)

    label_harga = QLabel("Rp 0")
    input_jumlah = QSpinBox()
    input_jumlah.setMinimum(1)
    label_total = QLabel("Rp 0")

    btn_tambah = QPushButton("Tambah")
    btn_hapus = QPushButton("Hapus")
    btn_simpan = QPushButton("Simpan Transaksi")
    
    btn_tambah.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_hapus.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_simpan.setCursor(Qt.CursorShape.PointingHandCursor)

    btn_tambah.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 6px 12px; border-radius: 8px; } QPushButton:hover { background-color: #45a049; } QPushButton:focus {border: none;}")
    btn_hapus.setStyleSheet("QPushButton { background-color: #F44336; color: white; padding: 6px 12px; border-radius: 8px; } QPushButton:hover { background-color: #e53935; } QPushButton:focus {border: none;}")
    btn_simpan.setStyleSheet("QPushButton { background-color: #1976D2; color: white; padding: 6px 12px; border-radius: 8px; } QPushButton:hover { background-color: #1565C0; } QPushButton:focus {border: none;}")

    formlabels = [
        ("Barang:", input_nama_barang),
        ("Harga:", label_harga),
        ("Jumlah:", input_jumlah),
        ("Total:", label_total)
    ]

    for text, widget in formlabels:
        if text:
            form_layout.addWidget(QLabel(text))
        form_layout.addWidget(widget)

    layout.addLayout(form_layout)

    button_layout = QHBoxLayout()
    button_layout.addWidget(btn_tambah)
    button_layout.addWidget(btn_hapus)
    button_layout.addWidget(btn_simpan)
    layout.addLayout(button_layout)

    table_transaksi = QTableWidget()
    table_transaksi.setColumnCount(6)
    table_transaksi.setHorizontalHeaderLabels(["Barang", "Jumlah", "Harga", "Total", "Tanggal", "Waktu"])
    layout.addWidget(table_transaksi)

    label_total_all = QLabel("Total Keseluruhan: Rp 0")
    layout.addWidget(label_total_all)

    def update_autocomplete(text):
        barang_dari_db = ambil_barang_dari_db()
        hasil = [b['nama'] for b in barang_dari_db if text.lower() in b['nama'].lower()]
        completer_model.setStringList(hasil)
        cocok = next((b for b in barang_dari_db if b['nama'].lower() == text.lower()), None)
        if cocok:
            update_harga_total(text, label_harga, label_total, input_jumlah)

    input_nama_barang.textChanged.connect(update_autocomplete)
    completer.activated.connect(lambda text: update_harga_total(text, label_harga, label_total, input_jumlah))

    input_jumlah.valueChanged.connect(lambda: update_harga_total(input_nama_barang.text(), label_harga, label_total, input_jumlah))

    table_transaksi.cellChanged.connect(lambda row, col: update_total_dan_grand_total(row, table_transaksi, label_total_all) if col == 1 else None)

    btn_tambah.clicked.connect(lambda: tambah_cb(input_nama_barang, input_jumlah, label_harga, table_transaksi, label_total_all))
    btn_hapus.clicked.connect(lambda: hapus_cb(table_transaksi, label_total_all))

    def simpan_dengan_waktu():
        try:
            items = []
            for row in range(table_transaksi.rowCount()):
                nama_item = table_transaksi.item(row, 0)
                jumlah_item = table_transaksi.item(row, 1)
                harga_item = table_transaksi.item(row, 2)
                subtotal_item = table_transaksi.item(row, 3)
                if not all([nama_item, jumlah_item, harga_item, subtotal_item]):
                    continue
                items.append({
                    "nama": nama_item.text(),
                    "jumlah": int(jumlah_item.text()),
                    "harga": parse_rp_to_int(harga_item.text()),
                    "subtotal": parse_rp_to_int(subtotal_item.text())
                })
            if not items:
                QMessageBox.warning(page, "Peringatan", "Tidak ada barang dalam transaksi.")
                return
            total_transaksi = parse_rp_to_int(label_total_all.text())
            main_window.simpan_transaksi(items, total_transaksi)
        except Exception as e:
            print("❌ Error saat menyimpan:", e)
            QMessageBox.critical(page, "Gagal", f"Gagal menyimpan transaksi:\n{str(e)}")

    btn_simpan.clicked.connect(simpan_dengan_waktu)

    page.input_nama_barang = input_nama_barang
    page.table_transaksi = table_transaksi
    page.setLayout(layout)

    def clear_form():
        input_nama_barang.clear()
        input_jumlah.setValue(1)
        table_transaksi.setRowCount(0)
        label_harga.setText("Rp 0")
        label_total.setText("Rp 0")
        label_total_all.setText("Total Keseluruhan: Rp 0")

    page.clear_form = clear_form
    return page
