# hrv/__init__.py
"""
Package HRV
===========

Expose une API simple pour le reste de l'application :

- clean_rr           : nettoyage des intervalles RR (outliers, ectopiques)
- compute_time_domain: métriques temporelles (SDNN, RMSSD)
- compute_spectral   : LF, HF, ratio LF/HF via Welch
- detrend_signal     : suppression tendance linéaire
- normalize_signal   : normalisation min-max (0..1)
"""

from .hrv_backend import clean_rr
from .time_domain import compute_time_domain
from .spectral import compute_spectral
from .utils import detrend_signal, normalize_signal

__all__ = [
    "clean_rr",
    "compute_time_domain",
    "compute_spectral",
    "detrend_signal",
    "normalize_signal",
]
