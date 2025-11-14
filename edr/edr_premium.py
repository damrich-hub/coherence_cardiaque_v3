# -*- coding: utf-8 -*-
"""
edr/edr_premium.py
------------------
Extraction Premium du signal respiratoire (EDR / RSA) à partir des intervalles RR.

Algorithme :
    - Interpolation RR -> 4 Hz
    - Calcul de la dérivée (RSA)
    - Filtrage passe-bande 0.07–0.40 Hz
    - Détection du pic spectral dominant (fréquence respiratoire)
    - Pondération de la qualité (SNR)
    - Sortie : fréquence (cpm), qualité (0–1), signal reconstruit (t, y)

Auteur : Damien × GPT-5
Version : V10 Premium
"""

import numpy as np
from scipy.signal import butter, filtfilt, welch
from scipy.interpolate import interp1d
from core.math_utils import clamp


class EDRPremium:
    """Classe pour l’estimation respiratoire premium à partir du signal RR."""

    def __init__(self, fs=4.0):
        self.fs = fs
        self.ema_cpm = None
        self.last_quality = 0.0
        self.last_signal = (None, None)

    # ------------------------------------------------------------
    def _welch_peak(self, y):
        """Recherche du pic spectral dominant (0.07–0.40 Hz)."""
        try:
            f, psd = welch(y, fs=self.fs, nperseg=min(256, len(y)))
            mask = (f >= 0.07) & (f <= 0.40)
            if not np.any(mask):
                return None, 0.0
            f_band, psd_band = f[mask], psd[mask]
            idx = np.argmax(psd_band)
            f0 = float(f_band[idx])
            peak = float(psd_band[idx])
            base = float(np.median(psd_band)) or 1e-12
            snr = peak / max(base, 1e-12)
            cpm = f0 * 60.0
            return (cpm, snr)
        except Exception:
            return None, 0.0

    # ------------------------------------------------------------
    def estimate(self, t, rr_ms):
        """
        Estime la respiration à partir des intervalles RR.
        Args:
            t (np.array): timestamps RR (s)
            rr_ms (np.array): intervalles RR (ms)
        Returns:
            (cpm, quality, (t_rel, y_norm)) or (None, 0.0, (None, None))
        """
        if len(rr_ms) < 30:
            return None, 0.0, (None, None)

        # 1. Interpolation à 4 Hz
        rr = np.array(rr_ms, float) / 1000.0
        try:
            t_reg = np.arange(t[0], t[-1], 1.0 / self.fs)
            rr_interp = interp1d(t, rr, fill_value="extrapolate")(t_reg)
        except Exception:
            return None, 0.0, (None, None)

        if len(rr_interp) < 64:
            return None, 0.0, (None, None)

        # 2. Dérivée (RSA)
        dy = np.gradient(rr_interp)

        # 3. Filtrage passe-bande
        b, a = butter(2, [0.07 / (self.fs / 2), 0.40 / (self.fs / 2)], btype="band")
        try:
            y_filt = filtfilt(b, a, dy)
        except Exception:
            return None, 0.0, (None, None)

        # 4. Pic spectral
        cpm, snr = self._welch_peak(y_filt)
        if cpm is None:
            return None, 0.0, (None, None)

        # 5. EMA + anti-saut
        if self.ema_cpm is not None:
            rel_diff = abs(cpm - self.ema_cpm) / max(1e-6, self.ema_cpm)
            if rel_diff > 0.25:
                cpm = self.ema_cpm + np.sign(cpm - self.ema_cpm) * 0.25 * self.ema_cpm
            self.ema_cpm = 0.8 * self.ema_cpm + 0.2 * cpm
        else:
            self.ema_cpm = cpm

        # 6. Normalisation du signal (pour affichage)
        y_norm = y_filt - np.mean(y_filt)
        std = np.std(y_norm)
        if std > 1e-6:
            y_norm = y_norm / (2 * std) + 0.5
        y_norm = np.clip(y_norm, 0, 1)

        t_rel = t_reg - t_reg[-1]
        mask = t_rel >= -20
        t_plot = t_rel[mask]
        y_plot = y_norm[mask]

        # 7. Qualité = SNR normalisée
        quality = clamp((snr - 1.0) / 4.0, 0.0, 1.0)
        self.last_quality = quality
        self.last_signal = (t_plot, y_plot)

        return float(self.ema_cpm), float(quality), (t_plot, y_plot)
