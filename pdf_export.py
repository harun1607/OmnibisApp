# pdf_export.py

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from matplotlib.backends.backend_agg import FigureCanvasAgg
from PyQt6.QtWidgets import QFileDialog, QMessageBox
import os

def save_grafik_as_image(canvas_widget, image_path):
    canvas_agg = FigureCanvasAgg(canvas_widget.fig)
    canvas_agg.draw()
    canvas_agg.print_png(image_path)

def export_filtered_to_pdf(laporan_page):
    mode = laporan_page.filter_combo.currentText()

    # Judul utama dan subjudul
    judul_utama = "Laporan Transaksi"
    subjudul = ""
    if mode == "Harian":
        dari = laporan_page.date_from.date().toString("dd MMM yyyy")
        sampai = laporan_page.date_to.date().toString("dd MMM yyyy")
        subjudul = f"Harian ({dari} - {sampai})"
    elif mode == "Mingguan":
        minggu = laporan_page.minggu_combo.lineEdit().text()
        bulan = laporan_page.bulan_combo.currentText()
        tahun = laporan_page.tahun_combo.currentText()
        subjudul = f"Mingguan ({minggu} - {bulan} {tahun})"
    elif mode == "Bulanan":
        bulan = laporan_page.bulan_bulanan_combo.lineEdit().text()
        tahun = laporan_page.tahun_combo.currentText()
        subjudul = f"Bulanan ({bulan} {tahun})"

    # Nama file
    filename = f"{judul_utama} {subjudul}".replace(" ", "_") + ".pdf"
    path, _ = QFileDialog.getSaveFileName(laporan_page, "Simpan Laporan Filter", filename, "PDF Files (*.pdf)")
    if not path:
        return

    try:
        c = pdf_canvas.Canvas(path, pagesize=A4)
        width, height = A4
        margin = 50

        # Logo
        logo_path = "logo1.png"  # Pastikan logo.png ada di direktori yang sama
        if os.path.exists(logo_path):
            c.drawImage(logo_path, margin, height - 60, width=40, height=40, mask='auto')

        # Judul dan subjudul
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - margin, judul_utama)

        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2, height - margin - 18, subjudul)

        # Garis pemisah
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.line(margin, height - margin - 28, width - margin, height - margin - 28)

        # Data tabel
        data = [["ID", "Tanggal", "Nama Barang", "Jumlah", "Harga", "Total"]]
        for row in range(laporan_page.table.rowCount()):
            row_data = []
            for col in range(laporan_page.table.columnCount()):
                item = laporan_page.table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        # Gaya tabel
        table = Table(data, colWidths=[45, 120, 130, 50, 60, 65])
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1f4e78")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        for i in range(1, len(data)):
            bgcolor = colors.whitesmoke if i % 2 == 0 else colors.lightgrey
            style.add('BACKGROUND', (0, i), (-1, i), bgcolor)
        table.setStyle(style)

        # Hitung posisi tabel
        y_pos = height - margin - 70
        row_height = 18
        table_height = len(data) * row_height
        table.wrapOn(c, width, height)
        table.drawOn(c, margin, y_pos - table_height)

        # Simpan grafik
        grafik_path = "temp_grafik.png"
        save_grafik_as_image(laporan_page.canvas, grafik_path)

        # Tempel grafik di bawah tabel
        grafik_y = y_pos - table_height - 220
        grafik_y = max(grafik_y, 60)
        c.drawImage(
            grafik_path,
            margin,
            grafik_y,
            width=width - 2 * margin,
            height=200,
            preserveAspectRatio=True,
            mask='auto'
        )

        # Footer
        c.setFont("Helvetica-Oblique", 8)
        c.setFillColor(colors.grey)
        c.drawRightString(width - margin, 30, "OmnibisApp • Halaman 1")

        c.showPage()
        c.save()

        if os.path.exists(grafik_path):
            os.remove(grafik_path)

    except Exception as e:
        QMessageBox.critical(laporan_page, "Export Gagal", f"Gagal mengekspor PDF: {str(e)}")