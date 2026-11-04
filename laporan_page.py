# laporan_page.py
import os
import sqlite3
import calendar
from datetime import datetime, timedelta, date
from collections import defaultdict

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QScrollArea, QAbstractItemView, QMessageBox,
    QDateEdit, QListView, QFileDialog
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtGui import QStandardItemModel, QStandardItem

from pdf_export import export_filtered_to_pdf


class GrafikCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=3, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)

    def plot_data(self, x, y, title):
        self.ax.clear()
        self.ax.bar(x, y, color='skyblue')
        self.ax.set_title(title)
        self.ax.set_xlabel("Periode")
        self.ax.set_ylabel("Total Transaksi")
        self.ax.grid(True)
        self.fig.tight_layout()
        self.draw()


class LaporanPage(QWidget):
    def __init__(self, filter_callback=None, export_callback=None):
        super().__init__()
        self.filter_callback = filter_callback
        self.export_callback = export_callback

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Laporan Transaksi")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1976D2;")
        layout.addWidget(title)

        # Filter controls
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Harian", "Mingguan", "Bulanan"])
        self.filter_combo.setCursor(Qt.CursorShape.PointingHandCursor)

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-6))
        self.date_from.setCursor(Qt.CursorShape.PointingHandCursor)

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCursor(Qt.CursorShape.PointingHandCursor)

        self.minggu_combo = QComboBox()
        self.minggu_combo.setView(QListView())
        self.minggu_combo.setModel(QStandardItemModel())
        self.minggu_combo.setEditable(True)
        self.minggu_combo.lineEdit().setReadOnly(True)
        self.minggu_combo.lineEdit().setPlaceholderText("Pilih Minggu")
        self.minggu_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.minggu_combo.setCursor(Qt.CursorShape.PointingHandCursor)

        for i in range(1, 5):
            item = QStandardItem(f"Minggu ke-{i}")
            item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
            self.minggu_combo.model().appendRow(item)
        self.minggu_combo.model().itemChanged.connect(self.update_minggu_selection)

        self.bulan_combo = QComboBox()
        self.bulan_combo.addItems([calendar.month_name[i] for i in range(1, 13)])
        self.bulan_combo.setCurrentIndex(QDate.currentDate().month() - 1)
        self.bulan_combo.setCursor(Qt.CursorShape.PointingHandCursor)

        self.bulan_bulanan_combo = QComboBox()
        self.bulan_bulanan_combo.setView(QListView())
        self.bulan_bulanan_combo.setModel(QStandardItemModel())
        self.bulan_bulanan_combo.setEditable(True)
        self.bulan_bulanan_combo.lineEdit().setReadOnly(True)
        self.bulan_bulanan_combo.lineEdit().setPlaceholderText("Pilih Bulan")
        self.bulan_bulanan_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.bulan_bulanan_combo.setCursor(Qt.CursorShape.PointingHandCursor)

        for i in range(1, 13):
            item = QStandardItem(calendar.month_name[i])
            item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
            self.bulan_bulanan_combo.model().appendRow(item)
        self.bulan_bulanan_combo.model().itemChanged.connect(self.update_bulan_selection)

        self.tahun_combo = QComboBox()
        current_year = QDate.currentDate().year()
        self.tahun_combo.addItems([str(current_year - 1), str(current_year), str(current_year + 1)])
        self.tahun_combo.setCurrentText(str(current_year))
        self.tahun_combo.setCursor(Qt.CursorShape.PointingHandCursor)

        # Buttons
        self.btn_filter = QPushButton("Filter")
        self.btn_filter.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_filter.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #1565C0; }
        """)

        self.btn_export_filter = QPushButton("Export Filter")
        self.btn_export_filter.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export_filter.setStyleSheet("""
            QPushButton {
                background-color: #43A047;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #388E3C; }
        """)
        self.btn_export_filter.clicked.connect(lambda: export_filtered_to_pdf(self))

        # Layouts
        self.filter_layout = QHBoxLayout()
        self.filter_layout.setSpacing(15)
        self.filter_layout.addWidget(QLabel("Filter:"))
        self.filter_layout.addWidget(self.filter_combo)
        self.filter_layout.addStretch()
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_filter)
        btn_layout.addWidget(self.btn_export_filter)
        self.filter_layout.addLayout(btn_layout)
        layout.addLayout(self.filter_layout)

        self.input_layout = QHBoxLayout()
        self.update_filter_inputs()
        layout.addLayout(self.input_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Tanggal", "Nama Barang", "Jumlah", "Harga", "Total"])
        layout.addWidget(self.table)

        self.canvas = GrafikCanvas(self)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        # Signals
        self.filter_combo.currentTextChanged.connect(self.update_filter_inputs)
        self.btn_filter.clicked.connect(self.tampilkan_laporan)

        # ✅ Tambahan: kosongkan laporan saat pertama kali buka
        self.reset_laporan()  # Kosongkan grafik & tabel

        # ✅ Tambahan: siapkan timer (15 menit, belum mulai)
        self.reset_timer = QTimer(self)
        self.reset_timer.timeout.connect(self.reset_laporan)

    def reset_laporan(self):
        """Kosongkan tabel dan grafik"""
        self.table.setRowCount(0)
        self.canvas.ax.clear()
        self.canvas.draw()
        QMessageBox.information(self, "Laporan Direset", "Laporan telah direset. Silakan pilih filter dan klik Filter lagi.")

    def tampilkan_laporan(self):
        """Versi lengkap: kode aslimu + tambahkan start/reset timer"""
        mode = self.filter_combo.currentText()
        conn = sqlite3.connect("OmnibisApp.db")
        cursor = conn.cursor()

        x_label = []
        y_total = []

        # === Laporan Harian ===
        if mode == "Harian":
            dari = self.date_from.date().toPyDate()
            sampai = self.date_to.date().toPyDate()
            delta = (sampai - dari).days
            if delta < 0 or delta >= 7:
                QMessageBox.warning(self, "Peringatan", "Untuk laporan harian, pilih maksimal 7 hari dan tidak boleh terbalik.")
                return
            cursor.execute("""
                SELECT DATE(tanggal), SUM(total)
                FROM transaksi
                WHERE DATE(tanggal) BETWEEN ? AND ?
                GROUP BY DATE(tanggal)
            """, (dari.strftime("%Y-%m-%d"), sampai.strftime("%Y-%m-%d")))
            rows = cursor.fetchall()
            data = {row[0]: row[1] for row in rows}
            for i in range(delta + 1):
                day = (dari + timedelta(days=i)).strftime("%Y-%m-%d")
                x_label.append(day[-2:])
                y_total.append(data.get(day, 0))
            title = "Laporan Harian"

        # === Laporan Mingguan ===
        elif mode == "Mingguan":
            checked_minggu = []
            for i in range(self.minggu_combo.model().rowCount()):
                item = self.minggu_combo.model().item(i)
                if item.checkState() == Qt.CheckState.Checked:
                    checked_minggu.append(i + 1)
            if not checked_minggu:
                QMessageBox.warning(self, "Peringatan", "Pilih minimal 1 minggu.")
                return
            bulan = list(calendar.month_name).index(self.bulan_combo.currentText())
            tahun = int(self.tahun_combo.currentText())
            first_day = date(tahun, bulan, 1)
            last_day_of_month = calendar.monthrange(tahun, bulan)[1]
            for minggu_ke in checked_minggu:
                start_day = first_day + timedelta(days=(minggu_ke - 1) * 7)
                end_day = start_day + timedelta(days=6)
                if start_day.day > last_day_of_month:
                    continue
                if end_day.month != bulan:
                    end_day = date(tahun, bulan, last_day_of_month)
                cursor.execute("""
                    SELECT SUM(total)
                    FROM transaksi
                    WHERE DATE(tanggal) BETWEEN ? AND ?
                """, (start_day.strftime("%Y-%m-%d"), end_day.strftime("%Y-%m-%d")))
                total = cursor.fetchone()[0] or 0
                x_label.append(f"Minggu {minggu_ke}")
                y_total.append(total)
                if 'dari' not in locals():
                    dari = start_day
                sampai = end_day
            title = f"Laporan Mingguan ({self.bulan_combo.currentText()})"

        # === Laporan Bulanan ===
        else:
            checked_bulan = []
            for i in range(self.bulan_bulanan_combo.model().rowCount()):
                item = self.bulan_bulanan_combo.model().item(i)
                if item.checkState() == Qt.CheckState.Checked:
                    checked_bulan.append(i + 1)
            if not checked_bulan:
                QMessageBox.warning(self, "Peringatan", "Pilih minimal 1 bulan.")
                return
            if len(checked_bulan) > 6:
                QMessageBox.warning(self, "Peringatan", "Pilih maksimal 6 bulan.")
                return
            tahun = int(self.tahun_combo.currentText())
            for bulan in checked_bulan:
                start_date = date(tahun, bulan, 1)
                last_day = calendar.monthrange(tahun, bulan)[1]
                end_date = date(tahun, bulan, last_day)
                cursor.execute("""
                    SELECT SUM(total)
                    FROM transaksi
                    WHERE DATE(tanggal) BETWEEN ? AND ?
                """, (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
                total = cursor.fetchone()[0] or 0
                x_label.append(f"{calendar.month_abbr[bulan]} {tahun}")
                y_total.append(total)
                if 'dari' not in locals():
                    dari = start_date
                sampai = end_date
            title = "Laporan Bulanan"

        # Tampilkan grafik
        self.canvas.plot_data(x_label, y_total, title)

        # Tampilkan tabel detail
        cursor.execute("""
            SELECT t.id, t.tanggal, p.nama, d.jumlah,
                   ROUND(d.subtotal * 1.0 / d.jumlah, 2) as harga,
                   d.subtotal
            FROM transaksi_detail d
            JOIN transaksi t ON d.id_transaksi = t.id
            JOIN produk p ON d.id_produk = p.id
            WHERE DATE(t.tanggal) BETWEEN ? AND ?
        """, (dari.strftime("%Y-%m-%d"), sampai.strftime("%Y-%m-%d")))
        transaksi_detail = cursor.fetchall()
        conn.close()
        self.table.setRowCount(len(transaksi_detail))
        for row_idx, row_data in enumerate(transaksi_detail):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_idx, col_idx, item)

        # ✅ Tambahan: restart timer 15 menit
        self.reset_timer.stop()
        self.reset_timer.start(15 * 60 * 1000)

    def update_filter_inputs(self):
        """Fungsimu aslinya tetap"""
        for i in reversed(range(self.input_layout.count())):
            self.input_layout.itemAt(i).widget().setParent(None)
        mode = self.filter_combo.currentText()
        spacing = 10
        if mode == "Harian":
            label_dari = QLabel("Dari:"); label_dari.setContentsMargins(0, 0, spacing, 0)
            label_sampai = QLabel("Sampai:"); label_sampai.setContentsMargins(spacing*2, 0, spacing, 0)
            self.input_layout.addWidget(label_dari); self.input_layout.addWidget(self.date_from)
            self.input_layout.addWidget(label_sampai); self.input_layout.addWidget(self.date_to)
        elif mode == "Mingguan":
            label_minggu = QLabel("Minggu:"); label_minggu.setContentsMargins(0, 0, spacing, 0)
            label_bulan = QLabel("Bulan:"); label_bulan.setContentsMargins(spacing*2, 0, spacing, 0)
            label_tahun = QLabel("Tahun:"); label_tahun.setContentsMargins(spacing*2, 0, spacing, 0)
            self.input_layout.addWidget(label_minggu); self.input_layout.addWidget(self.minggu_combo)
            self.input_layout.addWidget(label_bulan); self.input_layout.addWidget(self.bulan_combo)
            self.input_layout.addWidget(label_tahun); self.input_layout.addWidget(self.tahun_combo)
        elif mode == "Bulanan":
            label_bulan = QLabel("Bulan:"); label_bulan.setContentsMargins(0, 0, spacing, 0)
            label_tahun = QLabel("Tahun:"); label_tahun.setContentsMargins(spacing*2, 0, spacing, 0)
            self.input_layout.addWidget(label_bulan); self.input_layout.addWidget(self.bulan_bulanan_combo)
            self.input_layout.addWidget(label_tahun); self.input_layout.addWidget(self.tahun_combo)

    def update_minggu_selection(self, item):
        checked = []
        for i in range(self.minggu_combo.model().rowCount()):
            model_item = self.minggu_combo.model().item(i)
            if model_item.checkState() == Qt.CheckState.Checked:
                checked.append(model_item.text())
        if len(checked) > 4:
            item.setCheckState(Qt.CheckState.Unchecked)
            QMessageBox.warning(self, "Peringatan", "Pilih maksimal 4 minggu.")
        else:
            self.minggu_combo.lineEdit().setText(", ".join(checked))

    def update_bulan_selection(self, item):
        checked = []
        for i in range(self.bulan_bulanan_combo.model().rowCount()):
            model_item = self.bulan_bulanan_combo.model().item(i)
            if model_item.checkState() == Qt.CheckState.Checked:
                checked.append(model_item.text())
        if len(checked) > 6:
            item.setCheckState(Qt.CheckState.Unchecked)
            QMessageBox.warning(self, "Peringatan", "Pilih maksimal 6 bulan.")
        else:
            self.bulan_bulanan_combo.lineEdit().setText(", ".join(checked))
