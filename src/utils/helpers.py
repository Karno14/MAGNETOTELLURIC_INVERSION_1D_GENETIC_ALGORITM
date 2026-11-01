"""
Utility functions and helpers for Pemodelan MT 1D.
"""
from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, Optional
import numpy as np


def setup_logging(config: Dict[str, Any], script_dir: str) -> None:
    """
    Configure root logging for the application matching svc-time-table-report style.
    """
    logger = logging.getLogger()
    if logger.hasHandlers():
        logger.handlers.clear()

    log_path = config.get("LOG_FILE_PATH", "logs/app.log")
    full_log_path = os.path.join(script_dir, log_path)
    os.makedirs(os.path.dirname(full_log_path), exist_ok=True)

    log_level_name = str(config.get("LOG_LEVEL", "INFO")).upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    log_style = str(config.get("LOG_STYLE", "readable")).strip().lower()

    if log_style == "compact":
        log_format = "%(asctime)s | %(levelname).1s | %(message)s"
    elif log_style == "verbose":
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    else:  # readable
        log_format = "%(asctime)s | %(levelname)-5.5s | %(name)s | %(message)s"

    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_format, datefmt=date_format)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    file_handler = RotatingFileHandler(
        full_log_path,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.setLevel(log_level)


def save_and_plot_results(
    freq: np.ndarray,
    rho_obs: np.ndarray,
    rho_calc: np.ndarray,
    phase_calc: np.ndarray,
    rms_history: np.ndarray,
    save_dirs: list[str],
    show_plot: bool = True,
) -> None:
    """
    Plot and save MT inversion graphs: Apparent Resistivity, Phase, and RMS Error.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        logging.getLogger("mt_inversion").warning(
            "matplotlib is not installed; skipping plot generation."
        )
        return
    for d in save_dirs:
        os.makedirs(d, exist_ok=True)

    # 1. Grafik Hasil Pemodelan (Resistivitas Semu)
    plt.figure(figsize=(8, 6))
    plt.plot(np.log10(freq), rho_calc, "-", color="red", label="Respon Kalkulasi")
    plt.plot(np.log10(freq), rho_obs, "p", color="blue", label="Data Observasi")
    plt.xlabel("Frekuensi (log10 Hz)")
    plt.ylabel("Resistivitas Semu (Ohm.m)")
    plt.title("Perbandingan Data Observasi vs Kalkulasi")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    for d in save_dirs:
        plt.savefig(os.path.join(d, "hasil_pemodelan.PNG"), dpi=300, bbox_inches="tight")
    if show_plot:
        plt.show()
    plt.close()

    # 2. Grafik Fase Hasil Inversi
    plt.figure(figsize=(8, 6))
    plt.plot(np.log10(freq), phase_calc, "-", color="green", label="Fase Kalkulasi")
    plt.title("PHASA HASIL INVERSI")
    plt.xlabel("Frekuensi (log10 Hz)")
    plt.ylabel("Fase (Radian)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    for d in save_dirs:
        plt.savefig(os.path.join(d, "phasa.PNG"), dpi=300, bbox_inches="tight")
    if show_plot:
        plt.show()
    plt.close()

    # 3. Grafik Konvergensi RMS Error
    plt.figure(figsize=(8, 6))
    generations = np.arange(len(rms_history))
    plt.plot(generations, rms_history, "-", color="black", label="RMS Error")
    plt.title("GRAFIK RMS ERROR INVERSI")
    plt.xlabel("Generasi")
    plt.ylabel("RMS Error")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    for d in save_dirs:
        plt.savefig(os.path.join(d, "rms_error.PNG"), dpi=300, bbox_inches="tight")
    if show_plot:
        plt.show()
    plt.close()
