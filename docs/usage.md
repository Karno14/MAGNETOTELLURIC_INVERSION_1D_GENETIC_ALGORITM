# Usage Guide

## Getting Started

1. Masuk ke direktori repositori:
   ```bash
   cd D:\Python\Pemodelan_Pada_Data_Magnetotellurik
   ```

2. Buat dan aktifkan virtual environment (opsional/disarankan):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Pasang dependensi:
   ```bash
   pip install -r requirements.txt
   ```

4. Salin `.env.example` ke `.env` jika belum ada:
   ```bash
   copy .env.example .env
   ```

5. Jalankan aplikasi:
   - Menggunakan `main.py` di root:
     ```bash
     python main.py
     ```
   - Atau menggunakan module runner:
     ```bash
     python -m src.main
     ```
   - Mode headless / tanpa jendela plot (grafik tetap disimpan otomatis ke folder `grafik/` dan `data/output/`):
     ```bash
     python main.py --no-plot
     ```

## Sumber Data (Data Source)

Terdapat 2 opsi sumber data yang dapat dipilih melalui file `param_input.py` atau flag `--source`:

1. **Opsi PostgreSQL (Database Analytic)**:
   - Ambil data langsung dari tabel PostgreSQL `dad_dev.frequensi`.
   - Diatur di `param_input.py`:
     ```python
     DATA_SOURCE = "postgre"
     DB_QUERY = "SELECT * FROM dad_dev.frequensi;"
     ```
   - Pastikan tunnel SSH / database pada port `1244` aktif.

2. **Opsi File Teks (`data.txt`)**:
   - Ambil data dari file lokal `data/data.txt`.
   - Diatur di `param_input.py`:
     ```python
     DATA_SOURCE = "txt"
     DATA_TXT_PATH = "data/data.txt"
     ```

## Menjalankan Aplikasi

- **Mengikuti konfigurasi di `param_input.py`**:
  ```bash
  python src/main.py --job-code MT_INVERSION_1D_GA
  ```

- **Override sumber data via CLI**:
  ```bash
  # Menggunakan PostgreSQL (tabel dad_dev.frequensi):
  python src/main.py --job-code MT_INVERSION_1D_GA --source postgre

  # Menggunakan file teks lokal (data/data.txt):
  python src/main.py --job-code MT_INVERSION_1D_GA --source txt
  ```

- **Mode headless (tanpa window GUI plot)**:
  ```bash
  python src/main.py --job-code MT_INVERSION_1D_GA --no-plot
  ```

## Opsi Perintah Baris (CLI Options)

```text
--job-code          Kode job yang dieksekusi (default: MT_INVERSION_1D_GA)
--source            Pilihan sumber data: 'postgre' atau 'txt'
--data-path         Path menuju berkas data teks jika menggunakan source=txt (default: data/data.txt)
--max-iter          Jumlah generasi / iterasi GA (default: 100)
--population        Jumlah individu populasi (default: 50)
--layers            Jumlah lapisan bumi 1D (default: 7)
--crossover-rate    Probabilitas kawin silang / crossover (default: 0.8)
--mutation-rate     Probabilitas mutasi (default: 0.3)
--no-plot           Menonaktifkan tampilan window GUI matplotlib (otomatis simpan gambar)
```

Contoh kustomisasi eksekusi:
```bash
python main.py --max-iter 150 --population 60 --no-plot
```

