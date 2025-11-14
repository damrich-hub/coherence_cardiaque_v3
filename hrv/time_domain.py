# hrv/time_domain.py
"""
Time-domain HRV metrics.

Fonction principale :
- compute_time_domain(rr_ms) -> (sdnn, rmssd)
"""

from __future__ import annotations

from typing import Iterable, Tuple

import numpy as np


def compute_time_domain(rr_ms: Iterable[float]) -> Tuple[float, float]:
    """
    Calcule SDNN et RMSSD à partir d'une liste d'intervalles RR (en ms).

    Parameters
    ----------
    rr_ms : Iterable[float]
        Intervalles RR en millisecondes.

    Returns
    -------
    sdnn : float
        Écart-type des intervalles RR.
    rmssd : float
        Racine carrée de la moyenne des carrés des différences successives.
    """
    rr = np.asarray(list(rr_ms), dtype=float)
    if rr.size < 2:
        return 0.0, 0.0

    # SDNN : écart-type (on met ddof=1 pour l'estimateur non biaisé)
    sdnn = float(np.std(rr, ddof=1))

    # RMSSD
    diff = np.diff(rr)
    if diff.size == 0:
        rmssd = 0.0
    else:
        rmssd = float(np.sqrt(np.mean(diff * diff)))

    return sdnn, rmssd
