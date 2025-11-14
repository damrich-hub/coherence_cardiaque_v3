# respiration_edr.py
# Backend EDR basé sur NeuroKit2 : extraction d'un signal respiratoire
# lissé + estimation de la fréquence (cpm) et d'une qualité simple.

import numpy as np
from scipy.signal import welch
import neurokit2 as nk

from .helpers import interpolate_rr, normalize_signal, EDR_FS


def _clamp(x, xmin=0.0, xmax=1.0):
    return max(xmin, min(xmax, float(x)))


def extract_respiration_edr(t, rr_ms, fs=EDR_FS):
    """
    Estime un signal respiratoire (EDR) à partir des intervalles RR,
    en utilisant les briques de traitement de NeuroKit2.

    Pipeline :
        - interpolation RR -> 4 Hz
        - detrend via nk.signal_detrend
        - dérivée (RSA-like)
        - filtre passe-bande 0.07–0.40 Hz via nk.signal_filter
        - pic spectral (Welch) -> cpm + SNR
        - normalisation 0..1 pour affichage

    Parameters
    ----------
    t : np.ndarray
        Timestamps RR (s).
    rr_ms : np.ndarray
        Intervalles RR (ms).
    fs : float
        Fréquence d'échantillonnage cible (Hz), par défaut EDR_FS.

    Returns
    -------
    cpm : float ou None
        Fréquence respiratoire estimée (cycles/min).
    quality : float
        Qualité 0..1 (basée sur un SNR simple).
    (t_rel, y_norm) : tuple(np.ndarray, np.ndarray)
        Signal respiration estimé normalisé [0,1] sur les ~20 dernières secondes.
        Si échec : (None, None).
    """
    if t is None or rr_ms is None or len(rr_ms) < 30:
        return None, 0.0, (None, None)

    # 1) Interpolation RR -> 4 Hz
    t_reg, rr_interp = interpolate_rr(t, rr_ms)
    if t_reg is None or rr_interp is None or len(rr_interp) < 64:
        return None, 0.0, (None, None)

    # 2) Detrend avec NeuroKit2
    rr_detr = nk.signal_detrend(rr_interp)

    # 3) Dérivée (RSA-like)
    dy = np.gradient(rr_detr)

    # 4) Filtre passe-bande respiratoire via NeuroKit2
    try:
        y_filt = nk.signal_filter(
            dy,
            sampling_rate=fs,
            lowcut=0.07,
            highcut=0.40,
            method="butterworth",
            order=2,
        )
    except Exception:
        return None, 0.0, (None, None)

    # 5) Pic spectral (0.07–0.40 Hz)
    f, psd = welch(y_filt, fs=fs, nperseg=min(256, len(y_filt)))
    mask = (f >= 0.07) & (f <= 0.40)
    if not np.any(mask):
        return None, 0.0, (None, None)

    f_band, psd_band = f[mask], psd[mask]
    idx = int(np.argmax(psd_band))
    f0 = float(f_band[idx])
    peak = float(psd_band[idx])
    base = float(np.median(psd_band)) or 1e-12
    snr = peak / max(base, 1e-12)

    cpm = f0 * 60.0
    if not (4.0 <= cpm <= 20.0):
        return None, 0.0, (None, None)

    # 6) Normalisation 0..1 pour affichage
    y_norm = normalize_signal(y_filt)
    if y_norm is None:
        return None, 0.0, (None, None)

    # On garde ~20s pour l'affichage
    t_rel = t_reg - t_reg[-1]
    mask_20 = t_rel >= -20.0
    if not np.any(mask_20):
        return None, 0.0, (None, None)

    t_plot = t_rel[mask_20]
    y_plot = y_norm[mask_20]

    # 7) Qualité simple à partir du SNR (même logique que EDRPremium)
    quality = _clamp((snr - 1.0) / 4.0, 0.0, 1.0)

    return float(cpm), float(quality), (t_plot, y_plot)
