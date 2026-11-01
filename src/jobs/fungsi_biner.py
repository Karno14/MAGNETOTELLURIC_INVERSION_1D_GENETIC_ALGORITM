"""
Binary Genetic Algorithm module for 1D Magnetotelluric Inversion.
Provides operators: Initialization, Decoding, Roulette Wheel Selection,
Single-point Crossover, Generation Selection, and Mutation.
"""
from typing import Tuple
import numpy as np

from .fwd_mt import forward_mt, f_MT


def Inisiasi(
    n: int,
    n_lapis: int,
    n_bit: int,
    rho_min: float,
    rho_max: float,
    thick_min: float,
    thick_max: float,
    jlh_bit: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate initial population of n binary individuals and convert to decimal.

    Returns:
        Tuple of (individu_biner, individu_desimal)
    """
    individu_biner = np.zeros([n, jlh_bit])
    individu_desimal = np.zeros([n, (2 * n_lapis) - 1])

    # Random binary initialization
    for i in range(0, n):
        for j in range(0, jlh_bit):
            r = np.random.rand(1)
            if r >= 0.5:
                individu_biner[i, j] = 1.0

    # Binary to decimal decoding
    m_min = np.array([rho_min, thick_min])
    m_max = np.array([rho_max, thick_max])

    for i in range(0, n):
        for j in range(0, (2 * n_lapis) - 1):
            sumnya = 0.0
            for k in range(0, n_bit):
                jn = int(j * n_bit)
                sumnya += individu_biner[i, jn + k] * (2 ** -(k + 1))
            if j < ((2 * n_lapis) / 2):
                individu_desimal[i, j] = m_min[0] + (m_max[0] - m_min[0]) * sumnya
            else:
                individu_desimal[i, j] = m_min[1] + (m_max[1] - m_min[1]) * sumnya

    return individu_biner, individu_desimal


def Conv_desm(
    n: int,
    n_lapis: int,
    n_bit: int,
    individu_biner: np.ndarray,
    m_min: np.ndarray,
    m_max: np.ndarray,
) -> np.ndarray:
    """
    Decode binary matrix to decimal parameter model.
    """
    individu_desimal = np.zeros([n, (2 * n_lapis) - 1])
    for i in range(0, n):
        for j in range(0, (2 * n_lapis) - 1):
            sumnya = 0.0
            for k in range(0, n_bit):
                jn = int(j * n_bit)
                sumnya += individu_biner[i, jn + k] * (2 ** -(k + 1))
            if j < ((2 * n_lapis) / 2):
                individu_desimal[i, j] = m_min[0] + (m_max[0] - m_min[0]) * sumnya
            else:
                individu_desimal[i, j] = m_min[1] + (m_max[1] - m_min[1]) * sumnya
    return individu_desimal


def Milih(
    ndat: int,
    freq: np.ndarray,
    rho: np.ndarray,
    npopulasi: int,
    ind_desimal: np.ndarray,
    silang_rate: float,
    n_lapis: int,
) -> Tuple[np.ndarray, np.ndarray, int]:
    """
    Roulette Wheel Selection based on cumulative fitness.
    """
    d_cal_rho = np.zeros([npopulasi, ndat])
    d_sel_rho_app = np.zeros([npopulasi, ndat])
    d_sum = np.empty(npopulasi)
    d_rms = np.empty(npopulasi)
    fitness = np.zeros(npopulasi)
    probl = np.empty(npopulasi)
    prob_cum = np.empty(npopulasi)

    for ii in range(0, npopulasi):
        rho_app_calc, _ = forward_mt(freq, ind_desimal[ii, :], n_lapis)
        d_cal_rho[ii, :] = np.log10(rho_app_calc / rho)
        d_sel_rho_app[ii, :] = d_cal_rho[ii, :] * d_cal_rho[ii, :]
        d_sum[ii] = np.sum(d_sel_rho_app[ii, :])
        d_rms[ii] = np.sqrt(d_sum[ii] / ndat)

    e_min = np.min(d_rms)
    for i in range(0, npopulasi):
        fitness[i] = np.exp(-d_rms[i] / e_min)

    total_fitness = np.sum(fitness)
    for i in range(0, npopulasi):
        probl[i] = fitness[i] / total_fitness

    prob_cum[0] = probl[0]
    for ii in range(1, npopulasi):
        prob_cum[ii] = prob_cum[ii - 1] + probl[ii]

    jlh_kawin = int(np.floor(silang_rate * npopulasi))
    id_induk1 = np.zeros(jlh_kawin)
    id_induk2 = np.zeros(jlh_kawin)

    for i in range(0, jlh_kawin):
        r_acak = np.random.rand(1)
        id_induk = np.zeros(1)
        for j in range(0, npopulasi):
            if r_acak < prob_cum[j]:
                id_induk = np.append(id_induk, j)
        miy = np.shape(id_induk)[0]
        id_resize = id_induk[1:]
        id_induk1[i] = int(np.min(id_resize))
        id_induk2[i] = id_induk1[i] - 1
        if id_induk2[i] == -1:
            id_induk2[i] = npopulasi - 1

    return id_induk1, id_induk2, jlh_kawin


def KawinSilang(
    jlh_bit: int,
    ind_biner: np.ndarray,
    id_induk1: np.ndarray,
    id_induk2: np.ndarray,
    jlh_kawin: int,
) -> np.ndarray:
    """
    Single-point crossover between selected parents.
    """
    anak_1 = np.empty([jlh_kawin, jlh_bit])
    anak_2 = np.empty([jlh_kawin, jlh_bit])

    for ii in range(0, jlh_kawin):
        anak_1[ii, :] = ind_biner[int(id_induk1[ii]), :]
        anak_2[ii, :] = ind_biner[int(id_induk2[ii]), :]
        r_acak = np.random.randint(jlh_bit)
        anak_1[ii, r_acak:jlh_bit] = ind_biner[int(id_induk2[ii]), r_acak:jlh_bit]
        anak_2[ii, 0:r_acak] = ind_biner[int(id_induk1[ii]), 0:r_acak]

    ind_biner = np.append(ind_biner, anak_1, axis=0)
    ind_biner = np.append(ind_biner, anak_2, axis=0)
    return ind_biner


def Seleksi(
    ndat: int,
    freq: np.ndarray,
    rho: np.ndarray,
    npopulasi: int,
    ind_desimal: np.ndarray,
    n_lapis: int,
) -> Tuple[np.ndarray, float]:
    """
    Evaluate RMS error and rank individuals.
    """
    d_cal_rho = np.zeros([npopulasi, ndat])
    d_sel_rho_app = np.zeros([npopulasi, ndat])
    d_sum = np.empty(npopulasi)
    d_rms = np.empty(npopulasi)
    rank_indi = np.zeros([npopulasi, 2])

    for ii in range(0, npopulasi):
        rho_app_calc, _ = forward_mt(freq, ind_desimal[ii, :], n_lapis)
        d_cal_rho[ii, :] = np.log10(rho_app_calc / rho)
        d_sel_rho_app[ii, :] = d_cal_rho[ii, :] * d_cal_rho[ii, :]
        d_sum[ii] = np.sum(d_sel_rho_app[ii, :])
        d_rms[ii] = np.sqrt(d_sum[ii] / ndat)

    for jj in range(0, npopulasi):
        rank_indi[jj, 0] = jj
        rank_indi[jj, 1] = d_rms[jj]

    ranked_m = rank_indi[rank_indi[:, 1].argsort()[::1]]
    min_rms = float(np.min(d_rms))
    return ranked_m, min_rms


def Mutasi(
    ind_biner: np.ndarray,
    npopulasi: int,
    p_mutasi: float,
    jlh_bit: int,
) -> np.ndarray:
    """
    Bit-flip mutation.
    """
    jlh_ind_mut = int(np.floor(npopulasi * p_mutasi))
    for _ in range(0, jlh_ind_mut):
        r_acak1 = np.random.randint(npopulasi)
        r_acak2 = np.random.randint(jlh_bit)
        if ind_biner[r_acak1, r_acak2] == 0:
            ind_biner[r_acak1, r_acak2] = 1.0
        else:
            ind_biner[r_acak1, r_acak2] = 0.0
    return ind_biner

