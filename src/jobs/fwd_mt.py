"""
Forward modeling module for 1D Magnetotelluric (MT) layered earth.
Calculates apparent resistivity (Rho_ap) and impedance phase (phs_ap).
"""
import cmath
import math
from typing import Tuple
import numpy as np


def forward_mt(
    freq: np.ndarray,
    ind_desimal: np.ndarray,
    n_lapis: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute 1D MT forward response for layered earth model.

    Args:
        freq: 1D array of frequencies (Hz).
        ind_desimal: Model parameter array containing:
                     - Resistivities: rho_m[0:n_lapis] (Ohm.m)
                     - Thicknesses: thick[0:n_lapis-1] (m)
        n_lapis: Number of horizontal layers.

    Returns:
        Tuple of (apparent_resistivity, phase_in_radians)
    """
    rho_m = ind_desimal[0:n_lapis]
    thick = ind_desimal[n_lapis:(2 * n_lapis)]
    k_shape = freq.shape
    rho_ap = np.zeros(k_shape)
    phs_ap = np.zeros(k_shape)

    mu = 4 * np.pi * 1e-7  # Magnetic permeability of free space (H/m)

    for idx, frequency in enumerate(freq):
        w = 2 * np.pi * frequency  # Angular frequency (rad/s)

        # Characteristic impedance of the bottom half-space
        z0 = [0.0 + 0.0j] * n_lapis
        z0[n_lapis - 1] = cmath.sqrt(cmath.sqrt(-1) * w * mu * rho_m[n_lapis - 1])

        # Recursive upward propagation of impedance
        for j in range(n_lapis - 2, -1, -1):
            k = cmath.sqrt(cmath.sqrt(-1) * w * mu / rho_m[j])  # Wave number
            z0j = k * rho_m[j]
            rj = (z0j - z0[j + 1]) / (z0j + z0[j + 1])
            ej = cmath.exp(-2 * thick[j] * k)
            re = rj * ej
            zj = z0j * ((1 - re) / (1 + re))
            z0[j] = zj

        z_top = z0[0]
        z_real_mag = abs(z_top)

        rho_ap[idx] = (z_real_mag * z_real_mag) / (mu * w)
        phs_ap[idx] = math.atan2(z_top.imag, z_top.real)

    return rho_ap, phs_ap


# Alias for backward compatibility
f_MT = forward_mt

