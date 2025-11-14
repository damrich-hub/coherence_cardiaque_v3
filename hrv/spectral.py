import numpy as np
from scipy.signal import welch
from typing import Iterable, Dict, Optional

LF_BAND = (0.04, 0.15)
HF_BAND = (0.15, 0.40)
FS = 4.0  # fréquence d'échantillonnage interpolée


def detrend_signal(x: np.ndarray) -> np.ndarray:
    """Supprime la tendance linéaire pour améliorer le spectre."""
    return x - np.mean(x)


def _band_power(freqs, psd, band):
    mask = (freqs >= band[0]) & (freqs <= band[1])
    if not np.any(mask):
        return 0.0
    return np.trapz(psd[mask], freqs[mask])


def compute_spectral(rr_intervals_ms: Iterable[float]) -> Dict[str, Optional[float]]:
    """
    Calcule un spectre HRV complet.
    Retourne un dict :
      {
        "freq": ndarray,
        "power": ndarray,
        "lf": float,
        "hf": float,
        "peak_hf": float
      }
    """
    rr_list = list(rr_intervals_ms)
    n = len(rr_list)

    if n < 10:
        return {
            "freq": None,
            "power": None,
            "lf": 0.0,
            "hf": 0.0,
            "peak_hf": 0.0,
        }

    # Converti en secondes
    rr = np.asarray(rr_list, dtype=float) / 1000.0

    # Axe temporel cumulé
    t = np.cumsum(rr) - rr[0]
    if t[-1] <= 0:
        return {
            "freq": None,
            "power": None,
            "lf": 0.0,
            "hf": 0.0,
            "peak_hf": 0.0,
        }

    # Interpolation uniforme
    t_uniform = np.arange(0, t[-1], 1.0 / FS)
    if t_uniform.size < 8:
        return {
            "freq": None,
            "power": None,
            "lf": 0.0,
            "hf": 0.0,
            "peak_hf": 0.0,
        }

    rr_uniform = np.interp(t_uniform, t, rr)

    # Detrend
    rr_uniform = detrend_signal(rr_uniform)

    # PSD de Welch
    nperseg = min(256, len(rr_uniform))
    freqs, psd = welch(rr_uniform, fs=FS, nperseg=nperseg)

    # Puissances LF / HF
    lf = float(_band_power(freqs, psd, LF_BAND))
    hf = float(_band_power(freqs, psd, HF_BAND))

    # Pic HF = fréquence respiratoire
    mask_hf = (freqs >= HF_BAND[0]) & (freqs <= HF_BAND[1])
    if np.any(mask_hf):
        idx = np.argmax(psd[mask_hf])
        peak_hf = float(freqs[mask_hf][idx])
    else:
        peak_hf = 0.0

    return {
        "freq": freqs,
        "power": psd,
        "lf": lf,
        "hf": hf,
        "peak_hf": peak_hf,
    }

