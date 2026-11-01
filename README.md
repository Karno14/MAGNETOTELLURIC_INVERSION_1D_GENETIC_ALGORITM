# Pemodelan 1D Data Magnetotellurik Menggunakan Algoritma Genetika

Proyek ini melakukan inversi 1 Dimensi (1D) pada data Magnetotellurik (MT) untuk mengestimasi resistivitas dan ketebalan lapisan bumi menggunakan metode optimasi global Algoritma Genetika (Genetic Algorithm) dengan representasi biner.

Struktur repositori telah distandarisasi mengikuti pola arsitektur modular yang memisahkan konfigurasi, data observasi, fungsi rumus pemodelan, dan alur eksekusi aplikasi.

---

## 📁 Struktur Direktori

```text
Pemodelan_Pada_Data_Magnetotellurik/
├── config/
│   ├── __init__.py
│   ├── settings.py           # Modul pemuat konfigurasi (mendukung .env & YAML)
│   └── config/
│       └── local.yaml        # Parameter inversi, logging, dan path
├── data/
│   ├── data.txt              # Data observasi MT (Frekuensi vs Resistivitas Semu)
│   └── output/               # Folder output hasil kalkulasi dan grafik
├── docs/
│   ├── usage.md              # Panduan lengkap penggunaan
│   └── jurnal-karno.pdf      # Dokumen ilmiah acuan
├── logs/
│   └── .gitkeep              # Berkas log eksekusi (app.log)
├── grafik/                   # Gambar luaran grafik hasil inversi
│   ├── hasil_pemodelan.PNG
│   ├── phasa.PNG
│   └── rms_error.PNG
├── src/
│   ├── __init__.py
│   ├── main.py               # Entry point aplikasi utama dengan Argument Parser
│   ├── db/
│   │   ├── __init__.py
│   │   ├── connection.py     # Koneksi PostgreSQL analytic
│   │   └── repository/
│   │       ├── __init__.py
│   │       └── frequency_repository.py # Query tabel dad_dev.frequensi
│   ├── jobs/
│   │   ├── __init__.py
│   │   ├── fwd_mt.py         # Rumus forward modeling 1D MT (rekursi Cagniard/Wait)
│   │   ├── fungsi_biner.py   # Rumus & operator GA (inisiasi, seleksi, crossover, mutasi)
│   │   └── mt_inversion_job.py # Job processor pemecahan masalah inversi MT
│   └── utils/
│       ├── __init__.py
│       └── helpers.py        # Konfigurasi logging dan utilitas plotting
├── .env.example              # Contoh konfigurasi environment
├── .gitignore
├── param_input.py            # Konfigurasi parameter input & pilihan sumber data (postgre / txt)
├── requirements.txt          # Dependensi Python
└── setup.py                  # Konfigurasi instalasi paket
```

---

## 🚀 Cara Menjalankan

1. **Atur Sumber Data & Parameter**:
   Buka berkas `param_input.py` lalu sesuaikan pilihan `DATA_SOURCE`:
   - `"postgre"` : Mengambil data observasi dari PostgreSQL datamart_analytic (`dad_dev.frequensi`).
   - `"txt"`     : Mengambil data observasi dari berkas lokal `data/data.txt`.

2. **Jalankan Inversi**:
   - Menjalankan sesuai job code utama:
     ```bash
     python src/main.py --job-code MT_INVERSION_1D_GA
     ```
   - Override sumber data via CLI:
     ```bash
     python src/main.py --job-code MT_INVERSION_1D_GA --source postgre
     python src/main.py --job-code MT_INVERSION_1D_GA --source txt
     ```
   - Mode headless (tanpa window GUI plot):
     ```bash
     python src/main.py --job-code MT_INVERSION_1D_GA --no-plot
     ```

Lihat [docs/usage.md](docs/usage.md) untuk rincian opsi parameter *command line*.
