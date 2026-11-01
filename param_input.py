"""
File Pengaturan Parameter Input Pemodelan Magnetotellurik 1D (Algoritma Genetika)
================================================================================

File ini digunakan untuk mengatur sumber data dan seluruh parameter komputasi.
Silakan ubah variabel di bawah ini sesuai kebutuhan eksperimen.
"""

# ==============================================================================
# 1. SUMBER DATA OBSERVASI (DATA SOURCE)
# ==============================================================================
# Pilih salah satu dari dua opsi sumber data berikut:
#   - "postgre" : Mengambil data dari database PostgreSQL analytic (dad_dev.frequensi)
#   - "txt"     : Mengambil data dari berkas teks lokal (data/data.txt)
DATA_SOURCE = "postgre"

# Query SQL saat DATA_SOURCE = "postgre"
DB_QUERY = "SELECT * FROM dad_dev.frequensi;"

# Path berkas data saat DATA_SOURCE = "txt"
DATA_TXT_PATH = "data/data.txt"


# ==============================================================================
# 2. PARAMETER MODEL BUMI (1D LAYERED EARTH MODEL)
# ==============================================================================
N_LAPIS = 7              # Jumlah lapisan bumi (lapisan ke-7 adalah half-space/basement)
RHO_MIN = 0.0            # Batas minimum resistivitas (Ohm.m)
RHO_MAX = 90.0           # Batas maksimum resistivitas (Ohm.m)
THICK_MIN = 0.0          # Batas minimum ketebalan lapisan (meter)
THICK_MAX = 5000.0       # Batas maksimum ketebalan lapisan (meter)


# ==============================================================================
# 3. PARAMETER ALGORITMA GENETIKA (GENETIC ALGORITHM)
# ==============================================================================
N_POPULASI = 50          # Jumlah individu / ukuran populasi per generasi
N_BIT = 13               # Jumlah bit biner per parameter (resolusi kromosom)
MAX_ITER = 100           # Jumlah iterasi / generasi maksimum
CROSSOVER_RATE = 0.8     # Probabilitas kawin silang / pindah silang (crossover)
MUTATION_RATE = 0.3      # Probabilitas mutasi bit (mutation rate)


# ==============================================================================
# 4. PENGATURAN LUARAN & VISUALISASI
# ==============================================================================
SHOW_PLOT = True            # True: tampilkan window grafik interaktif; False: mode headless
OUTPUT_DIR = "data/output"  # Folder penyimpanan data hasil inversi
GRAFIK_DIR = "grafik"       # Folder penyimpanan grafik hasil pemodelan (PNG)


def get_param_input() -> dict:
    """Mengembalikan seluruh parameter input dalam bentuk dictionary."""
    return {
        "DATA_SOURCE": DATA_SOURCE,
        "DB_QUERY": DB_QUERY,
        "DATA_TXT_PATH": DATA_TXT_PATH,
        "N_LAPIS": N_LAPIS,
        "RHO_MIN": RHO_MIN,
        "RHO_MAX": RHO_MAX,
        "THICK_MIN": THICK_MIN,
        "THICK_MAX": THICK_MAX,
        "N_POPULASI": N_POPULASI,
        "N_BIT": N_BIT,
        "MAX_ITER": MAX_ITER,
        "CROSSOVER_RATE": CROSSOVER_RATE,
        "MUTATION_RATE": MUTATION_RATE,
        "SHOW_PLOT": SHOW_PLOT,
        "OUTPUT_DIR": OUTPUT_DIR,
        "GRAFIK_DIR": GRAFIK_DIR,
    }
