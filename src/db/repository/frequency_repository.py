"""
Database repository helpers for querying MT frequency observation data.
"""
from __future__ import annotations

import logging
from typing import Tuple
import numpy as np

logger = logging.getLogger(__name__)


def get_frequency_data(
    conn,
    query: str = "SELECT * FROM dad_dev.frequensi;",
) -> Tuple[np.ndarray, np.ndarray, int]:
    """
    Fetch frequency and apparent resistivity data from PostgreSQL analytic table.

    Args:
        conn: psycopg2 connection object.
        query (str): SQL query to execute (default: SELECT * FROM dad_dev.frequensi;).

    Returns:
        Tuple of (freq, rho_dat, ndat):
            - freq: 1D array of frequencies (Hz)
            - rho_dat: 1D array of apparent resistivity (Ohm.m)
            - ndat: number of data points
    """
    logger.info(f"Executing query on analytic database: {query}")
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            if not rows:
                raise ValueError(f"Query returned 0 rows from '{query}'.")

            col_names = [desc[0].lower() for desc in cur.description]
            logger.info(f"Retrieved {len(rows)} records from PostgreSQL. Columns: {col_names}")

            # 1. Deteksi kolom frekuensi
            freq_candidates = ["freq", "frequency", "frequensi", "frekuensi", "f"]
            freq_idx = None
            for cand in freq_candidates:
                if cand in col_names:
                    freq_idx = col_names.index(cand)
                    break
            if freq_idx is None:
                freq_idx = 0  # Default ke kolom pertama jika tidak ditemukan

            # 2. Deteksi kolom resistivitas semu (rho)
            rho_candidates = [
                "rho",
                "rho_app",
                "rho_dat",
                "apparent_resistivity",
                "resistivitas",
                "resistivitas_semu",
                "res",
            ]
            rho_idx = None
            for cand in rho_candidates:
                if cand in col_names:
                    rho_idx = col_names.index(cand)
                    break
            if rho_idx is None:
                rho_idx = 1 if len(col_names) > 1 else 0

            logger.info(
                f"Using column '{col_names[freq_idx]}' (col #{freq_idx}) as Frequency, "
                f"and '{col_names[rho_idx]}' (col #{rho_idx}) as Apparent Resistivity."
            )

            freq_list = []
            rho_list = []
            for r in rows:
                if r[freq_idx] is not None and r[rho_idx] is not None:
                    freq_list.append(float(r[freq_idx]))
                    rho_list.append(float(r[rho_idx]))

            freq = np.array(freq_list, dtype=float)
            rho_dat = np.array(rho_list, dtype=float)
            ndat = len(freq)

            if ndat == 0:
                raise ValueError("No valid numeric frequency/resistivity values found in rows.")

            return freq, rho_dat, ndat

    except Exception:
        logger.exception(f"Error executing frequency data query: {query}")
        raise

