"""
normalizers.py
----------------
Normalisation des métriques HRV pour le calcul du score global.

Ce module est utilisé par :
- global_score.py
- les sous-scores
"""

from score.utils import clamp, safe_float
import math


def norm_ratio(lf, hf):
    """Normalisation du ratio LF/HF avec stabilisation log."""
    if hf <= 1e-12:
        return 0.0
    r = lf / hf
    # 1 − |log10(r)| -> donne une valeur entre 0 et 1 si r ≈ 1
    return clamp(1.0 - abs(math.log10(max(1e-8, r))), 0, 1)


def norm_hf_fraction(lf, hf):
    """HF / (LF + HF). Normalise la prédominance parasympathique."""
    s = lf + hf
    if s <= 0:
        return 0.0
    return clamp(hf / s, 0, 1)


def norm_rmssd(x):
    """Normalise RMSSD avec un plafond ~80 ms."""
    return clamp(safe_float(x) / 80.0, 0, 1)


def norm_sdnn(x):
    """Normalise SDNN avec un plafond ~100 ms."""
    return clamp(safe_float(x) / 100.0, 0, 1)


def norm_lf(x):
    """Normalise LF avec un plafond typique ~500 ms²."""
    return clamp(safe_float(x) / 500.0, 0, 1)
