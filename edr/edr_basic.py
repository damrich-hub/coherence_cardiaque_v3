"""
edr_basic.py
-------------
Méthodes simples d'estimation de la respiration :
- edr via Welch (pic spectral)
- Génération d'un sinus à la fréquence détectée
"""

import numpy as np
from scipy.signal import welch

from .helpers import interpolate_rr, compute_rsa, normalize_signal, EDR_FS


def estimate_cpm_welch(t, rr_ms):
    """
    Estime la fréquence respiratoire (cpm) via Welch sur le RR interpolé.
    """
    t_reg, y = interpolate_rr(t, rr_ms)
    if y is None or len(y) < 64:
        return None

    f, psd = welch(y, fs=EDR_FS, nperseg=min(256, len(y)))
    mask = (f >= 0.07) & (f <= 0.40)

    if not np.any(mask):
        return None

    fr = f[mask]
    pr = psd[mask]
    f_peak = fr[np.argmax(pr)]
    cpm = float(f_peak * 60.0)

    if 4 <= cpm <= 20:
        return cpm
    return None


def generate_sinus(cpm, duration=20.0, points=400):
    """
    Génère une courbe sinus normalisée [0,1] pour affichage.
    """
    if cpm is None:
        return None, None

    f = cpm / 60.0
    t = np.linspace(-duration, 0.0, points)
    sig = 0.5 + 0.5 * np.sin(2 * np.pi * f * t)
    return t, sig
