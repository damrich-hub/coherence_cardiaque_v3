# hrv/spectral.py
"""
Analyse spectrale HRV – méthode Welch (LF / HF / ratio).

Fonction principale :
- compute_spectral(rr_intervals_ms) -> (lf, hf, ratio)
"""

from __future__ import annotations

from typing import Iterable, Tuple

import numpy as np
from scipy.signal import welch

from .utils import detrend_signal

# Bandes standard HF/LF en Hz
LF_BAND = (0.04, 0.15)
HF_BAND = (0.15, 0.40)

# Fréquence d’échantillonnage après interpolation (Hz)
FS = 4.0


def compute_spectral(rr_intervals_ms: Iterable[float]) -> Tuple[float, float, float]:
    """
    Calcule les puissances LF, HF et le ratio LF/HF à partir des intervalles RR.

    Parameters
    ----------
    rr_intervals_ms : Iterable[float]
        Intervalles RR en millisecondes.

    Returns
    -------
    lf : float
    hf : float
    ratio : float
    """
    rr_list = list(rr_intervals_ms)
    if len(rr_list) < 10:
        return 0.0, 0.0, 0.0

    # Convertir en secondes
    rr = np.asarray(rr_list, dtype=float) / 1000.0

    # Temps cumulé
    t = np.cumsum(rr) - rr[0]
    if t[-1] <= 0:
        return 0.0, 0.0, 0.0

    # Interpolation régulière
    t_uniform = np.arange(0, t[-1], 1.0 / FS)
    if t_uniform.size < 4:
        return 0.0, 0.0, 0.0

    rr_uniform = np.interp(t_uniform, t, rr)

    # Détrending léger
    rr_uniform = detrend_signal(rr_uniform)

    # Welch
    nperseg = min(256, len(rr_uniform))
    if nperseg < 16:
        return 0.0, 0.0, 0.0

    freqs, psd = welch(rr_uniform, fs=FS, nperseg=nperseg)

    # Intégration des bandes
    lf = _band_power(freqs, psd, LF_BAND)
    hf = _band_power(freqs, psd, HF_BAND)

    ratio = lf / hf if hf > 1e-12 else 0.0

    return float(lf), float(hf), float(ratio)


def _band_power(freqs: np.ndarray, psd: np.ndarray, band) -> float:
    """Intègre la puissance du PSD dans une bande donnée."""
    fmin, fmax = band
    mask = (freqs >= fmin) & (freqs <= fmax)
    if not np.any(mask):
        return 0.0
    return float(np.trapz(psd[mask], freqs[mask]))

