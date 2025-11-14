"""
helpers.py
-----------
Fonctions utilitaires utilisées par les différents algorithmes EDR :
- interpolation régulière (RR → 4 Hz)
- calcul RSA (dérivée du signal RR)
- filtrage passe-bande 0.07–0.40 Hz (fréquence respiratoire)
- normalisation 0..1 pour affichage
"""

import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import butter, filtfilt


# Fréquence de resampling (Hz) pour tous les traitements EDR
EDR_FS = 4.0


# ---------------------------------------------------------
# Interpolation RR -> signal régulier à 4 Hz
# ---------------------------------------------------------
def interpolate_rr(t, rr_ms):
    """
    Interpole les intervalles RR en un signal échantillonné régulièrement à 4 Hz.

    Parameters
    ----------
    t : np.ndarray
        Timestamps des RR (secondes).
    rr_ms : np.ndarray
        Intervalles RR en millisecondes.

    Returns
    -------
    t_reg, y_reg : np.ndarray
        Temps réguliers et signal RR interpolé (en secondes).
        (None, None) en cas d'échec.
    """
    if t is None or rr_ms is None or len(t) < 2 or len(rr_ms) < 2:
        return None, None

    rr_s = np.asarray(rr_ms, dtype=float) / 1000.0

    try:
        t_start = float(t[0])
        t_end = float(t[-1])
        if t_end <= t_start:
            return None, None

        t_reg = np.arange(t_start, t_end, 1.0 / EDR_FS)
        if t_reg.size < 2:
            return None, None

        f = interp1d(t, rr_s, kind="linear", fill_value="extrapolate")
        y = f(t_reg)
        return t_reg, y
    except Exception:
        return None, None


# ---------------------------------------------------------
# Calcul RSA (dérivée RR + filtrage passe-bande)
# ---------------------------------------------------------
def compute_rsa(y, fs=EDR_FS):
    """
    Calcule le signal RSA en dérivant RR, puis en appliquant un filtre 0.07–0.40 Hz.

    Parameters
    ----------
    y : np.ndarray
        Signal RR interpolé (s).
    fs : float
        Fréquence d'échantillonnage (Hz).

    Returns
    -------
    y_rsa : np.ndarray ou None
    """
    if y is None or len(y) < 10:
        return None

    dy = np.gradient(np.asarray(y, dtype=float))

    # Filtre passe-bande (0.07–0.40 Hz)
    b, a = butter(2, [0.07 / (fs / 2), 0.40 / (fs / 2)], btype="band")

    try:
        y_f = filtfilt(b, a, dy)
        return y_f
    except Exception:
        return None


# ---------------------------------------------------------
# Normalisation du signal pour affichage (0..1)
# ---------------------------------------------------------
def normalize_signal(sig):
    """
    Normalise un signal autour de [-1,1] puis le met en [0,1].

    Utile pour :
    - courbe respiration réelle
    - courbe sinus
    """
    if sig is None:
        return None

    sig = np.asarray(sig, dtype=float)
    if sig.size == 0:
        return None

    sig = sig - np.mean(sig)
    std = np.std(sig)
    if std < 1e-6:
        # Série quasi constante → ligne à 0.5
        return np.zeros_like(sig) + 0.5

    sig = sig / (2 * std) + 0.5
    return np.clip(sig, 0, 1)
