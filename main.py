#file main.py
import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame, QTableWidgetItem,
    QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QPixmap, QIcon, QColor
from dashboard_page import create_dashboard_page
from transaksi_page import create_transaksi_page
from laporan_page import LaporanPage
from barang_page import create_barang_page
from init_db import init_db
from datetime import datetime
import random

class AnimatedButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self._bg_color = QColor("white")
        self.default_color = QColor("white")
        self.hover_color = QColor("#3B82F6")  # Biru muda
        self.setStyleSheet(self.build_stylesheet(self._bg_color))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setCheckable(True)

    def build_stylesheet(self, color):
        text_color = 'white' if color != QColor('white') else '#333'
        return f"""
            QPushButton {{
                padding: 10px;
                text-align: left;
                font-weight: 500;
                font-size: 14px;
                background-color: {color.name()};
                color: {text_color};
                border: none;
                border-radius: 6px;
                transition: background-color 0.3s ease;
            }}
        """


    def enterEvent(self, event):
        self.animate_color(self.hover_color)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.isChecked():
            self.animate_color(self.default_color)
        super().leaveEvent(event)

    def animate_color(self, target_color):
        self.anim = QPropertyAnimation(self, b"bg_color")
        self.anim.setDuration(150)
        self.anim.setStartValue(self._bg_color)
        self.anim.setEndValue(target_color)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim.start()

    def get_bg_color(self):
        return self._bg_color

    def set_bg_color(self, color):
        self._bg_color = color
        self.setStyleSheet(self.build_stylesheet(self._bg_color))

    bg_color = pyqtProperty(QColor, get_bg_color, set_bg_color)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        init_db()

        # Atur judul jendela dan icon (logo di pojok kiri atas window)
        self.setWindowTitle("Omnibis App")
        self.setWindowIcon(QIcon("logo.png"))  
        self.setGeometry(100, 100, 1200, 800)

        self.barang_list = []
        self.load_barang_from_db()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        self.header = self.create_header()
        self.main_layout.addWidget(self.header)

        self.content_layout = QHBoxLayout()
        self.main_layout.addLayout(self.content_layout)

        self.sidebar = self.create_sidebar()
        self.sidebar.setFixedWidth(200)
        self.content_layout.addWidget(self.sidebar)

        self.pages = QStackedWidget()
        self.content_layout.addWidget(self.pages)

        self.page_dashboard = create_dashboard_page()
        self.page_transaksi = create_transaksi_page(main_window=self)

        self.page_laporan = LaporanPage(
            filter_callback=self.filter_laporan,
            export_callback=self.export_laporan
        )
        self.page_barang = create_barang_page(
            tambah_cb=self.tambah_barang_database,
            hapus_cb=self.hapus_barang_data,
            edit_cb=self.edit_barang_data,
            generate_id_cb=self.generate_random_id,
            get_all_barang_cb=self.ambil_semua_barang
        )

        self.pages.addWidget(self.page_dashboard)
        self.pages.addWidget(self.page_transaksi)
        self.pages.addWidget(self.page_laporan)
        self.pages.addWidget(self.page_barang)

        self.update_table_barang()
        self.update_combo_barang()

    def create_header(self):
        header = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)

        self.btn_toggle = QPushButton("☰")
        self.btn_toggle.setFixedSize(40, 40)
        self.btn_toggle.setStyleSheet("""
            font-size: 20px;
            border: none;
            background-color: transparent;
            color: white;
        """)
        self.btn_toggle.clicked.connect(self.toggle_sidebar)

        self.label_title = QLabel("Dashboard")
        self.label_title.setStyleSheet("font-size: 20px; font-weight: 600; color: white;")

        layout.addWidget(self.btn_toggle)
        layout.addSpacing(10)
        layout.addWidget(self.label_title)
        layout.addStretch()
        
        header.setLayout(layout)
        header.setStyleSheet("background-color: #3B82F6; border-bottom: 1px solid #CCC;")  
        return header

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setStyleSheet("background-color: #FFFFFF; border-right: 1px solid #CCC;")
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        self.sidebar_buttons = []
        
        def create_button(name):
            btn = AnimatedButton(name)
            self.sidebar_buttons.append(btn)
            return btn
        btn_dashboard = QPushButton("Dashboard")
        btn_transaksi = QPushButton("Transaksi")
        btn_laporan = QPushButton("Laporan")
        btn_barang = QPushButton("Barang")

        btn_dashboard.clicked.connect(lambda: self.switch_page(0, btn_dashboard))
        btn_transaksi.clicked.connect(lambda: self.switch_page(1, btn_transaksi))
        btn_laporan.clicked.connect(lambda: self.switch_page(2, btn_laporan))
        btn_barang.clicked.connect(lambda: self.switch_page(3, btn_barang))


        for btn in [btn_dashboard, btn_transaksi, btn_laporan, btn_barang]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("padding: 10px; text-align: left;")
            layout.addWidget(btn)

        layout.addStretch()
        sidebar.setLayout(layout)
        btn_dashboard.setChecked(True)
        return sidebar

    def toggle_sidebar(self):
        if self.sidebar.isVisible():
            self.sidebar.hide()
            self.btn_toggle.setText("☰")
        else:
            self.sidebar.show()
            self.btn_toggle.setText("✕")

    def switch_page(self, index, active_button):
        self.pages.setCurrentIndex(index)
        self.label_title.setText(active_button.text())

        for btn in self.sidebar_buttons:
            btn.setChecked(btn == active_button)

            self.load_barang_from_db()
            self.update_combo_barang()

    def load_barang_from_db(self):
        conn = sqlite3.connect("OmnibisApp.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nama, harga FROM produk")
        rows = cursor.fetchall()
        conn.close()

        self.barang_list = [{'id': row[0], 'nama': row[1], 'harga': row[2]} for row in rows]

    def update_table_barang(self):
        table = self.page_barang.findChild(QWidget, "table_barang")
        if not table:
            return
        table.setRowCount(0)
        for barang in self.barang_list:
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(barang['id']))
            table.setItem(row, 1, QTableWidgetItem(barang['nama']))
            table.setItem(row, 2, QTableWidgetItem(f"Rp {barang['harga']}"))

    def update_combo_barang(self):
        if hasattr(self.page_transaksi, "update_combo_barang"):
            self.page_transaksi.update_combo_barang(self.barang_list)

    def update_harga(self, combo_barang, label_harga, label_total, input_jumlah, barang_list):
        selected = combo_barang.text()
        barang = next((b for b in barang_list if b['nama'].lower() == selected.lower()), None)
        if barang:
            harga = barang['harga']
            label_harga.setText(f"Rp {harga:,.0f}")
            label_total.setText(f"Rp {harga * input_jumlah.value()}")
        else:
            label_harga.setText("Rp 0")
            label_total.setText("Rp 0")
            

    def update_total(self, combo_barang, label_harga, label_total, input_jumlah, barang_list):
        selected = combo_barang.currentText()
        harga = next((b['harga'] for b in barang_list if b['nama'].lower() == selected.lower()), 0)
        label_total.setText(f"Rp {harga * input_jumlah.value()}")

    def tambah_barang_transaksi(self, input_nama_barang, input_jumlah, label_harga, table_transaksi):
        jumlah = input_jumlah.value()
        nama = input_nama_barang.text()
        barang = next((b for b in self.barang_list if b['nama'].lower() == nama.lower()), None)
        if not barang:
            return
        harga = barang['harga']
        print(f"DEBUG: nama={nama}, jumlah={jumlah}, harga={harga}, tipe harga={type(harga)}")
    
        total = harga * jumlah
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
        label_harga.setText(f"Rp {harga:,}".replace(",", "."))
        for row in range(table_transaksi.rowCount()):
            if table_transaksi.item(row, 0).text().lower() == nama.lower():
            
                jumlah_lama = int(table_transaksi.item(row, 1).text())
                jumlah_baru = jumlah + jumlah_lama
                total_baru = harga * jumlah_baru
                table_transaksi.setItem(row, 1, QTableWidgetItem(str(jumlah_baru)))
                table_transaksi.setItem(row, 3, QTableWidgetItem(f"Rp {total_baru}"))
                table_transaksi.setItem(row, 4, QTableWidgetItem(waktu))
                return
        row = table_transaksi.rowCount()
        table_transaksi.insertRow(row)
    
        table_transaksi.setItem(row, 0, QTableWidgetItem(nama))
        table_transaksi.setItem(row, 1, QTableWidgetItem(str(jumlah)))
        table_transaksi.setItem(row, 2, QTableWidgetItem(f"Rp {harga:,}".replace(",", ".")))
        table_transaksi.setItem(row, 3, QTableWidgetItem(f"Rp {total:,}".replace(",", ".")))
        table_transaksi.setItem(row, 4, QTableWidgetItem(waktu))

    def tambah_barang_database(self, id_barang, nama_barang, harga_barang, table_barang):
        try:
            conn = sqlite3.connect("OmnibisApp.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO produk (id, nama, harga) VALUES (?, ?, ?)",
                           (id_barang, nama_barang, harga_barang))
            conn.commit()
            conn.close()

            self.load_barang_from_db()  # reload data barang dari DB
            self.update_table_barang()  # update UI tabel barang
            self.update_combo_barang()  # update combo di transaksi
            QMessageBox.information(None, "Sukses", "Barang berhasil ditambahkan.")
        except sqlite3.IntegrityError:
            QMessageBox.warning(None, "Peringatan", "ID Barang sudah ada.")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Gagal menambahkan barang: {e}")


    def hapus_barang_data(self, id_barang):
        try:
            conn = sqlite3.connect("OmnibisApp.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM produk WHERE id = ?", (id_barang,))
            conn.commit()
            conn.close()
            self.load_barang_from_db()
            self.update_table_barang()
            self.update_combo_barang()
            QMessageBox.information(self, "Berhasil", "Barang berhasil dihapus.")
        except Exception as e:
            QMessageBox.critical(self, "Gagal", f"Gagal menghapus barang:\n{e}")
    
   
        
    def simpan_transaksi(self, items, total_transaksi=None):
        if not items:
            QMessageBox.warning(self, "Validasi", "Tidak ada item dalam transaksi.")
            return

        for item in items:
            if item["jumlah"] <= 0 or item["subtotal"] <= 0:
                QMessageBox.warning(self, "Validasi", f"Data tidak valid pada barang '{item['nama']}'.")
                return

        try:
            conn = sqlite3.connect("OmnibisApp.db")
            cursor = conn.cursor()

            tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Langkah 1: Simpan transaksi awal (dengan total 0)
            cursor.execute(
                "INSERT INTO transaksi (tanggal, total) VALUES (?, ?)",
                (tanggal, 0)
            )
            id_transaksi = cursor.lastrowid

            # Langkah 2: Simpan detail dan hitung total
            total_fix = 0
            for item in items:
                produk = next((b for b in self.barang_list if b['nama'].lower() == item['nama'].lower()), None)
                if produk:
                    cursor.execute(
                        '''INSERT INTO transaksi_detail 
                           (id_transaksi, id_produk, jumlah, subtotal) 
                           VALUES (?, ?, ?, ?)''',
                        (id_transaksi, produk['id'], item['jumlah'], item['subtotal'])
                    )
                    total_fix += item['subtotal']

            # Langkah 3: Update total ke transaksi
            cursor.execute(
                "UPDATE transaksi SET total = ? WHERE id = ?",
                (total_fix, id_transaksi)
            )

            conn.commit()
            conn.close()

            QMessageBox.information(self, "Berhasil", "Transaksi berhasil disimpan.")

            if hasattr(self.page_transaksi, "clear_form"):
                self.page_transaksi.clear_form()

        except Exception as e:
            QMessageBox.critical(self, "Gagal", f"Gagal menyimpan transaksi:\n{e}")


    def update_table_item(self, item, table):
        pass  # Dapat dikembangkan sesuai kebutuhan

    def filter_laporan(self, dari, sampai, table):
        pass  # Diimplementasikan di laporan_page.py

    def export_laporan(self):
        pass  # Diimplementasikan di laporan_page.py

    def edit_barang_data(self, new_id, nama, harga, old_id):
        try:
            conn = sqlite3.connect("OmnibisApp.db")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE produk SET id = ?, nama = ?, harga = ? WHERE id = ?",
                (new_id, nama, harga, old_id)
            )
            conn.commit()
            conn.close()
    
            self.load_barang_from_db()
            self.update_table_barang()
            self.update_combo_barang()
    
            QMessageBox.information(self, "Sukses", "Barang berhasil diperbarui.")
        except Exception as e:
            QMessageBox.critical(self, "Gagal", f"Gagal mengedit barang:\n{e}")


    def generate_random_id(self):
        return f"{random.randint(10000, 99999)}"
    
    def ambil_semua_barang(self):
        conn = sqlite3.connect("OmnibisApp.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nama, harga FROM produk")
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "nama": r[1], "harga": r[2]} for r in rows]
    
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())