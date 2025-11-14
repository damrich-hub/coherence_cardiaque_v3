# -*- coding: utf-8 -*-
"""
score/components.py
-------------------
Sous-scores et synchronisation cœur–respiration (Sync%).
"""

import numpy as np
from core.math_utils import clamp


def compute_sync_score(rr_intervals: list[float],
                       resp_cpm: float | None,
                       resp_quality: float | None) -> float:
    """
    Calcule un pourcentage de synchronisation cœur–respiration.
    Combine :
        - la stabilité de la fréquence respiratoire
        - la qualité du signal respiratoire
        - la cohérence de phase approximée (simplifiée)
    Retourne un score entre 0 et 100 (%).
    """
    if not rr_intervals or resp_cpm is None or resp_cpm <= 0:
        return 0.0

    # Approximation : stabilité de respiration (6 cpm = cible)
    sync_freq = max(0.0, 1.0 - abs(resp_cpm - 6.0) / 6.0)

    # Variabilité stable (cohérence cardiaque régulière)
    rr = np.asarray(rr_intervals, dtype=float)
    if len(rr) < 10:
        return 0.0

    rr_std = np.std(rr)
    rr_mean = np.mean(rr)
    stability = 1.0 - clamp(rr_std / (rr_mean * 0.2), 0.0, 1.0)

    # Pondération respiration / stabilité / qualité
    q = resp_quality or 0.0
    sync = 100.0 * (0.5 * sync_freq + 0.3 * stability + 0.2 * q)
    return clamp(sync, 0.0, 100.0)
