# OmnibisApp – Aplikasi Desktop Pencatatan Transaksi

## Deskripsi Proyek

**OmnibisApp** merupakan aplikasi desktop berbasis Python yang dikembangkan untuk membantu proses pencatatan dan pengelolaan transaksi secara terstruktur. Aplikasi ini menyediakan fitur pengelolaan data barang, pencatatan transaksi, pemantauan informasi melalui dashboard, serta penyusunan laporan transaksi.

OmnibisApp dirancang dengan antarmuka grafis sehingga pengguna dapat mengakses berbagai fitur melalui menu navigasi yang tersedia tanpa harus berinteraksi langsung dengan database.

Aplikasi ini menggunakan SQLite sebagai penyimpanan data lokal dan dilengkapi visualisasi grafik serta fitur ekspor laporan ke dalam format PDF.

## Fitur Utama

### 1. Dashboard
- Menampilkan halaman utama aplikasi.
- Menyediakan navigasi ke berbagai fitur pengelolaan.
- Menjadi pusat akses informasi aplikasi.

### 2. Pengelolaan Data Barang
- Menambahkan data barang.
- Mengubah informasi barang.
- Menghapus data barang.
- Menampilkan daftar barang yang tersimpan.

### 3. Pencatatan Transaksi
- Mencatat transaksi penjualan.
- Memilih barang dari daftar produk.
- Mengelola jumlah barang dalam transaksi.
- Menghitung subtotal dan total transaksi.
- Menyimpan data transaksi beserta detailnya.

### 4. Laporan Transaksi
- Menampilkan data transaksi dalam bentuk tabel.
- Menyediakan filter laporan berdasarkan periode harian, mingguan, dan bulanan.
- Menampilkan visualisasi data transaksi menggunakan grafik.
- Menyediakan fitur ekspor laporan berdasarkan filter yang dipilih.

### 5. Ekspor Laporan PDF
- Mengekspor laporan transaksi ke format PDF.
- Menyertakan informasi transaksi dalam bentuk tabel.
- Menyertakan visualisasi grafik pada laporan.
- Memungkinkan pengguna menentukan lokasi penyimpanan dokumen.

## Teknologi yang Digunakan

| Kategori | Teknologi |
|---|---|
| Bahasa Pemrograman | Python |
| Framework GUI | PyQt6 |
| Database | SQLite |
| Visualisasi Data | Matplotlib |
| Ekspor Dokumen | ReportLab |
| Pengelolaan Versi | Git dan GitHub |

## Struktur Proyek

```text
OmnibisApp/
│
├── main.py
│
├── dashboard_page.py
│
├── barang_page.py
│
├── transaksi_page.py
│
├── laporan_page.py
│
├── pdf_export.py
│
├── init_db.py
│
├── OmnibisApp.db
│
├── logo.png
│
├── logo1.png
│
└── README.md
```

**Keterangan file:**

| File | Fungsi |
|---|---|
| `main.py` | Entry point dan pengelolaan jendela utama aplikasi. |
| `dashboard_page.py` | Mengatur tampilan halaman dashboard. |
| `barang_page.py` | Mengelola data barang. |
| `transaksi_page.py` | Mengelola proses pencatatan transaksi. |
| `laporan_page.py` | Menampilkan dan memfilter laporan transaksi. |
| `pdf_export.py` | Mengatur proses ekspor laporan ke PDF. |
| `init_db.py` | Membuat dan menginisialisasi struktur database. |
| `OmnibisApp.db` | Database SQLite untuk menyimpan data aplikasi. |

## Instalasi dan Konfigurasi

### 1. Persyaratan Sistem

Pastikan perangkat telah memiliki:
- Python 3.10 atau versi yang lebih baru.
- pip (Python Package Installer).
- Sistem operasi yang mendukung aplikasi desktop PyQt6.

### 2. Clone Repository

Jalankan perintah berikut pada terminal:

```bash
git clone https://github.com/harun1607/OmnibisApp.git

cd OmnibisApp
```

### 3. Membuat Virtual Environment

Buat lingkungan virtual Python agar dependensi proyek terpisah dari instalasi Python utama.

```bash
python -m venv venv
```

Aktifkan virtual environment pada Windows:

```bash
venv\Scripts\activate
```

Untuk Linux atau macOS:

```bash
source venv/bin/activate
```

### 4. Instalasi Dependensi

Instal library yang dibutuhkan aplikasi:

```bash
pip install PyQt6 matplotlib reportlab
```

### 5. Menjalankan Aplikasi

Setelah seluruh dependensi terpasang, jalankan aplikasi melalui file utama:

```bash
python main.py
```

Database SQLite akan diinisialisasi oleh aplikasi melalui modul `init_db.py` ketika aplikasi dijalankan.

## Database

OmnibisApp menggunakan SQLite sebagai sistem manajemen basis data lokal.

Database memiliki tiga tabel utama:

| Nama Tabel | Fungsi |
|---|---|
| `produk` | Menyimpan identitas, nama, dan harga barang. |
| `transaksi` | Menyimpan tanggal dan total transaksi. |
| `transaksi_detail` | Menyimpan rincian barang, jumlah, dan subtotal setiap transaksi. |

Relasi antartabel digunakan untuk menghubungkan transaksi dengan detail barang yang tercatat.

## Pengembang

**Harun Fitrah Arrahim**

GitHub: [@harun1607](https://github.com/harun1607)

## Repository

[OmnibisApp – GitHub](https://github.com/harun1607/OmnibisApp)