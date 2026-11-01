"""
MT 1D Genetic Algorithm Inversion Job Processor.
Supports dual observation data sources: PostgreSQL analytic DB and local data.txt.
"""
from __future__ import annotations

import logging
import os
import time
from typing import Any, Dict
import numpy as np

try:
    import MAGNETOTELLURIC_INVERSION_1D_GENETIC_ALGORITM.src.jobs.param_input as param_input
except ImportError:
    param_input = None

from .fwd_mt import forward_mt
from .fungsi_biner import (
    Inisiasi,
    Conv_desm,
    Milih,
    KawinSilang,
    Seleksi,
    Mutasi,
)
from ..utils.helpers import save_and_plot_results
from ..db.connection import get_connection
from ..db.repository.frequency_repository import get_frequency_data


class MTInversionJob:
    """
    Job class executing 1D MT inversion using Genetic Algorithm.
    Follows structured lifecycle: context management, logging, and execution.
    """

    def __init__(
        self,
        job_code: str,
        config: Dict[str, Any],
        logger: logging.Logger,
    ):
        self.job_code = job_code
        self.config = config
        self.logger = logger
        self.script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

        # 1. Muat parameter default dari param_input.py jika tersedia
        params = param_input.get_param_input() if param_input and hasattr(param_input, "get_param_input") else {}

        # 2. Ambil parameter dengan hierarki: config/CLI > param_input > default
        self.data_source = str(
            self.config.get("DATA_SOURCE", params.get("DATA_SOURCE", "postgre"))
        ).strip().lower()

        self.db_query = self.config.get(
            "DB_QUERY", params.get("DB_QUERY", "SELECT * FROM dad_dev.frequensi;")
        )

        data_txt = self.config.get("DATA_TXT_PATH", params.get("DATA_TXT_PATH", "data/data.txt"))
        self.data_txt_path = (
            data_txt if os.path.isabs(data_txt) else os.path.join(self.script_dir, data_txt)
        )

        self.n_populasi = int(self.config.get("N_POPULASI", params.get("N_POPULASI", 50)))
        self.n_lapis = int(self.config.get("N_LAPIS", params.get("N_LAPIS", 7)))
        self.n_bit = int(self.config.get("N_BIT", params.get("N_BIT", 13)))
        self.rho_min = float(self.config.get("RHO_MIN", params.get("RHO_MIN", 0.0)))
        self.rho_max = float(self.config.get("RHO_MAX", params.get("RHO_MAX", 90.0)))
        self.thick_min = float(self.config.get("THICK_MIN", params.get("THICK_MIN", 0.0)))
        self.thick_max = float(self.config.get("THICK_MAX", params.get("THICK_MAX", 5000.0)))
        self.max_iter = int(self.config.get("MAX_ITER", params.get("MAX_ITER", 100)))
        self.crossover_rate = float(self.config.get("CROSSOVER_RATE", params.get("CROSSOVER_RATE", 0.8)))
        self.mutation_rate = float(self.config.get("MUTATION_RATE", params.get("MUTATION_RATE", 0.3)))
        self.show_plot = bool(self.config.get("SHOW_PLOT", params.get("SHOW_PLOT", True)))

        out_dir = self.config.get("OUTPUT_DIR", params.get("OUTPUT_DIR", "data/output"))
        grafik_dir = self.config.get("GRAFIK_DIR", params.get("GRAFIK_DIR", "grafik"))
        self.output_dirs = [
            out_dir if os.path.isabs(out_dir) else os.path.join(self.script_dir, out_dir),
            grafik_dir if os.path.isabs(grafik_dir) else os.path.join(self.script_dir, grafik_dir),
        ]

    def __enter__(self):
        self.logger.info(f"Starting job: {self.job_code}")
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - getattr(self, "start_time", time.time())
        if exc_type:
            self.logger.error(f"Job {self.job_code} failed with error: {exc_val}", exc_info=True)
        else:
            self.logger.info(f"Job {self.job_code} completed successfully in {duration:.2f}s")
        return False

    def load_data(self) -> tuple[np.ndarray, np.ndarray, int]:
        """
        Load observation data based on DATA_SOURCE:
          - "postgre": Fetch from PostgreSQL datamart_analytic (dad_dev.frequensi)
          - "txt": Load from local data file (e.g. data/data.txt)
        """
        if self.data_source in ["postgre", "postgresql", "postgres", "db"]:
            self.logger.info(
                f"[DATA SOURCE: POSTGRESQL] Mengambil data dari tabel '{self.db_query}'..."
            )
            conn = None
            try:
                conn = get_connection(self.config)
                freq, rho_dat, ndat = get_frequency_data(conn, query=self.db_query)
                self.logger.info(
                    f"Berhasil memuat {ndat} titik data observasi dari PostgreSQL datamart_analytic."
                )
                return freq, rho_dat, ndat
            except Exception as err:
                self.logger.error(
                    f"Gagal mengambil data dari PostgreSQL: {err}. "
                    "Pastikan SSH tunnel / server database di port 1244 aktif, "
                    "atau ubah DATA_SOURCE = 'txt' pada param_input.py untuk menggunakan data lokal."
                )
                raise
            finally:
                if conn is not None and not conn.closed:
                    conn.close()
                    self.logger.info("Database connection closed.")
        else:
            self.logger.info(f"[DATA SOURCE: TXT FILE] Membaca data dari: {self.data_txt_path}")
            if not os.path.exists(self.data_txt_path):
                raise FileNotFoundError(f"File data teks tidak ditemukan di: {self.data_txt_path}")

            d_obs = np.loadtxt(self.data_txt_path)
            freq = d_obs[:, 0]
            rho_dat = d_obs[:, 1]
            ndat = len(freq)
            self.logger.info(f"Berhasil memuat {ndat} titik data observasi dari file teks.")
            return freq, rho_dat, ndat

    def process(self) -> Dict[str, Any]:
        """Execute the Genetic Algorithm inversion process."""
        freq, rho_dat, ndat = self.load_data()

        jlh_bit = self.n_bit * ((2 * self.n_lapis) - 1)
        m_min = np.array([self.rho_min, self.thick_min])
        m_max = np.array([self.rho_max, self.thick_max])

        self.logger.info(
            f"Inisiasi GA: populasi={self.n_populasi}, lapis={self.n_lapis}, "
            f"bit_per_param={self.n_bit}, total_bit={jlh_bit}, max_iter={self.max_iter}"
        )

        ind_biner, ind_desimal = Inisiasi(
            self.n_populasi,
            self.n_lapis,
            self.n_bit,
            self.rho_min,
            self.rho_max,
            self.thick_min,
            self.thick_max,
            jlh_bit,
        )

        rms_history = np.zeros(self.max_iter)
        id_terpilih = None

        self.logger.info("Memulai iterasi Algoritma Genetika...")
        for iterasi in range(self.max_iter):
            # 1. Roulette Wheel Selection
            id_induk1, id_induk2, jlh_kawin = Milih(
                ndat, freq, rho_dat, self.n_populasi, ind_desimal, self.crossover_rate, self.n_lapis
            )

            # 2. Crossover (Kawin Silang)
            ind_biner = KawinSilang(jlh_bit, ind_biner, id_induk1, id_induk2, jlh_kawin)
            m, _ = ind_biner.shape
            ind_desimal = Conv_desm(m, self.n_lapis, self.n_bit, ind_biner, m_min, m_max)

            # 3. Seleksi & Ranking
            id_terpilih, d_rms = Seleksi(ndat, freq, rho_dat, m, ind_desimal, self.n_lapis)

            ind_terpilih_mat = np.zeros([m, jlh_bit])
            for i in range(self.n_populasi):
                ind_terpilih_mat[i, :] = ind_biner[int(id_terpilih[i, 0]), :]

            # 4. Mutasi
            ind_biner = Mutasi(ind_terpilih_mat, self.n_populasi, self.mutation_rate, jlh_bit)
            ind_biner = np.delete(ind_biner, np.s_[self.n_populasi:m], 0)
            ind_desimal = Conv_desm(self.n_populasi, self.n_lapis, self.n_bit, ind_biner, m_min, m_max)

            rms_history[iterasi] = d_rms

            if (iterasi + 1) % 10 == 0 or iterasi == self.max_iter - 1:
                self.logger.info(f"Generasi {iterasi + 1}/{self.max_iter} - Best RMS: {d_rms:.6f}")

        # Individu Terbaik generasi terakhir (indeks 0 setelah ranking seleksi)
        best_model = ind_desimal[0, :]
        rho_calc, phase_calc = forward_mt(freq, best_model, self.n_lapis)

        self.logger.info("=== Hasil Inversi Akhir ===")
        self.logger.info(f"Final Best RMS Error: {rms_history[-1]:.6f}")
        self.logger.info(f"Resistivitas (Ohm.m): {np.round(best_model[:self.n_lapis], 2)}")
        self.logger.info(
            f"Ketebalan Lapisan (m): {np.round(best_model[self.n_lapis:(2 * self.n_lapis) - 1], 2)}"
        )

        # Simpan & plot hasil
        save_and_plot_results(
            freq,
            rho_dat,
            rho_calc,
            phase_calc,
            rms_history,
            save_dirs=self.output_dirs,
            show_plot=self.show_plot,
        )

        return {
            "best_model": best_model,
            "final_rms": rms_history[-1],
            "rms_history": rms_history,
            "rho_calc": rho_calc,
            "phase_calc": phase_calc,
        }
