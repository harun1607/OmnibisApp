#file barang_page.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor

def create_barang_page(tambah_cb, hapus_cb, edit_cb, generate_id_cb, get_all_barang_cb):
    page = QWidget()
    layout = QVBoxLayout()

    # Scrollable content wrapper
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    content_widget = QWidget()
    content_layout = QVBoxLayout(content_widget)

    # Form input barang
    form_layout = QHBoxLayout()

    label_id = QLabel("ID:")
    input_id = QLineEdit()
    input_id.setReadOnly(True)

    label_nama = QLabel("Nama:")
    input_nama = QLineEdit()

    label_harga = QLabel("Harga:")
    input_harga = QLineEdit()

    btn_generate_id = QPushButton("Generate ID")
    btn_generate_id.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    btn_generate_id.setStyleSheet("background-color: #888; color: white; padding: 5px 10px; border-radius: 6px;")

    btn_tambah = QPushButton("Tambah")
    btn_tambah.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    btn_tambah.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px 10px; border-radius: 6px;")

    btn_hapus = QPushButton("Hapus")
    btn_hapus.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    btn_hapus.setStyleSheet("background-color: #f44336; color: white; padding: 5px 10px; border-radius: 6px;")

    btn_edit = QPushButton("Edit")
    btn_edit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    btn_edit.setStyleSheet("background-color: #2196F3; color: white; padding: 5px 10px; border-radius: 6px;")

    form_layout.addWidget(label_id)
    form_layout.addWidget(input_id)
    form_layout.addWidget(btn_generate_id)
    form_layout.addWidget(label_nama)
    form_layout.addWidget(input_nama)
    form_layout.addWidget(label_harga)
    form_layout.addWidget(input_harga)
    form_layout.addWidget(btn_tambah)
    form_layout.addWidget(btn_hapus)
    form_layout.addWidget(btn_edit)

    content_layout.addLayout(form_layout)

    # Kolom pencarian
    search_layout = QHBoxLayout()
    search_label = QLabel("Cari:")
    search_input = QLineEdit()
    search_input.setPlaceholderText("Ketik nama barang...")
    search_layout.addWidget(search_label)
    search_layout.addWidget(search_input)
    content_layout.addLayout(search_layout)

    # Tabel barang
    table_barang = QTableWidget()
    table_barang.setObjectName("table_barang")
    table_barang.setColumnCount(3)
    table_barang.setHorizontalHeaderLabels(["ID", "Nama", "Harga"])
    table_barang.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    table_barang.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    content_layout.addWidget(table_barang)

    scroll_area.setWidget(content_widget)
    layout.addWidget(scroll_area)

    # Fungsi untuk memuat data barang ke tabel
    def muat_data_barang():
        keyword = search_input.text().lower()
        table_barang.setRowCount(0)
        for barang in get_all_barang_cb():
            if keyword and keyword not in barang['nama'].lower():
                continue
            row = table_barang.rowCount()
            table_barang.insertRow(row)
            table_barang.setItem(row, 0, QTableWidgetItem(barang['id']))
            table_barang.setItem(row, 1, QTableWidgetItem(barang['nama']))
            harga_formatted = f"Rp {barang['harga']:,}".replace(",", ".")
            table_barang.setItem(row, 2, QTableWidgetItem(harga_formatted))

    muat_data_barang()

    # Validasi input
    def validasi_input(require_id=False):
        if require_id and not input_id.text().strip():
            QMessageBox.warning(page, "Peringatan", "Silakan klik 'Generate ID' terlebih dahulu sebelum menambah barang.")
            return False
        nama = input_nama.text().strip()
        if not nama:
            QMessageBox.warning(page, "Peringatan", "Nama barang harus diisi.")
            return False
        if len(nama) < 3:
            QMessageBox.warning(page, "Peringatan", "Nama barang minimal 3 karakter.")
            return False
        import re
        if not re.match(r'^[\w\s]+$', nama):
            QMessageBox.warning(page, "Peringatan", "Nama barang hanya boleh berisi huruf, angka, dan spasi.")
            return False
        try:
            harga = int(input_harga.text())
            if harga < 0:
                QMessageBox.warning(page, "Peringatan", "Harga harus positif.")
                return False
            if harga > 10_000_000:
                QMessageBox.warning(page, "Peringatan", "Harga tidak boleh lebih dari Rp 10.000.000.")
                return False
        except ValueError:
            QMessageBox.warning(page, "Peringatan", "Harga harus berupa angka bulat tanpa titik/koma.")
            return False
        return True

    # Reset form input
    def reset_form():
        input_id.clear()
        input_nama.clear()
        input_harga.clear()

    # Fungsi edit (update data + update ID kalau perlu)
    def on_edit_clicked():
        selected = table_barang.currentRow()
        if selected >= 0:
            old_id = table_barang.item(selected, 0).text().strip()

            if not input_id.text().strip():
                new_id = generate_id_cb()
                input_id.setText(new_id)
            else:
                new_id = input_id.text().strip()

            if validasi_input():
                edit_cb(
                    new_id,
                    input_nama.text().strip(),
                    int(input_harga.text()),
                    old_id
                )
                muat_data_barang()
                reset_form()
        else:
            QMessageBox.warning(page, "Peringatan", "Pilih barang yang ingin diedit.")

    # Fungsi generate ID (manual, user klik tombol)
    def generate_new_id():
        new_id = generate_id_cb()
        input_id.setText(new_id)

        selected = table_barang.currentRow()
        if selected >= 0:
            old_id = table_barang.item(selected, 0).text().strip()
            nama = input_nama.text().strip()
            try:
                harga = int(input_harga.text())
            except ValueError:
                QMessageBox.warning(page, "Peringatan", "Harga harus berupa angka.")
                return

            edit_cb(new_id, nama, harga, old_id)
            table_barang.setItem(selected, 0, QTableWidgetItem(new_id))
            QMessageBox.information(page, "Info", "ID barang berhasil diperbarui.")
        else:
            QMessageBox.information(page, "Info", "ID baru berhasil dibuat. Silakan tambahkan barang atau pilih barang untuk mengganti ID.")

    # Hubungkan tombol ke fungsi
    btn_generate_id.clicked.connect(generate_new_id)

    btn_tambah.clicked.connect(lambda: (
        tambah_cb(input_id.text(), input_nama.text().strip(), int(input_harga.text()), table_barang),
        muat_data_barang(),
        reset_form()
    ) if validasi_input(require_id=True) else None)

    btn_edit.clicked.connect(on_edit_clicked)

    btn_hapus.clicked.connect(lambda: (
        hapus_cb(input_id.text()),
        muat_data_barang(),
        reset_form()
    ) if input_id.text().strip() else QMessageBox.warning(page, "Peringatan", "Pilih barang yang ingin dihapus."))

    # Saat user pilih baris → isi form
    def isi_form():
        selected = table_barang.currentRow()
        if selected >= 0:
            input_id.setText(table_barang.item(selected, 0).text())
            input_nama.setText(table_barang.item(selected, 1).text())
            harga_str = table_barang.item(selected, 2).text().replace("Rp ", "").replace(".", "")
            input_harga.setText(harga_str)

    search_input.textChanged.connect(muat_data_barang)
    table_barang.itemSelectionChanged.connect(isi_form)

    page.setLayout(layout)
    page.muat_data_barang = muat_data_barang
    return page