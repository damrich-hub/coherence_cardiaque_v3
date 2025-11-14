# hrv/hrv_backend.py
"""
Backend HRV : nettoyage RR + wrapper optionnel autour de hrvanalysis.

- clean_rr(rr_ms)        : filtre les RR aberrants + ectopiques
"""

from __future__ import annotations

from typing import Iterable, List

import numpy as np

try:
    # Le package pip est "hrv-analysis", le module python est "hrvanalysis"
    import hrvanalysis as hrv_lib  # type: ignore
except Exception:  # pragma: no cover
    hrv_lib = None


def _np_array(rr_ms: Iterable[float]) -> np.ndarray:
    """Convertit en array float64."""
    return np.asarray(list(rr_ms), dtype=float)


def clean_rr(rr_ms: Iterable[float]) -> List[float]:
    """
    Nettoie une série d'intervalles RR (ms).

    Stratégie :
    1. Conversion en numpy
    2. Si hrvanalysis dispo → utilise son pipeline (outliers + ectopiques + interpolation)
    3. Sinon → fallback simple (filtre [300, 2000] ms et sigma-clipping)

    Parameters
    ----------
    rr_ms : Iterable[float]
        Intervalles RR en millisecondes.

    Returns
    -------
    List[float]
        Liste nettoyée d'intervalles RR (ms).
    """
    rr = _np_array(rr_ms)
    if rr.size == 0:
        return []

    # --- Cas 1 : hrvanalysis disponible ---
    if hrv_lib is not None:
        try:
            # Suppression des outliers grossiers (selon hrvanalysis)
            rr_no_out = hrv_lib.remove_outliers(
                rr_intervals=rr,
                low_rri=300,
                high_rri=2000
            )

            # Correction des battements ectopiques
            rr_no_ect = hrv_lib.remove_ectopic_beats(
                rr_intervals=rr_no_out,
                method="malik"
            )

            # Interpolation des trous
            rr_interp = hrv_lib.interpolate_nan(
                rr_intervals=rr_no_ect,
                method="linear"
            )

            clean = np.asarray(rr_interp, dtype=float)
            clean = clean[np.isfinite(clean)]
            return clean.tolist()
        except Exception:
            # Si quelque chose se passe mal, on tombe sur le fallback
            pass

    # --- Cas 2 : Fallback simple maison ---
    # Filtre très grossier sur les valeurs admissibles
    mask = (rr >= 300.0) & (rr <= 2000.0)
    rr = rr[mask]
    if rr.size < 4:
        return rr.tolist()

    # Sigma-clipping léger
    med = float(np.median(rr))
    mad = float(np.median(np.abs(rr - med))) or 1.0
    z = 0.6745 * (rr - med) / mad
    mask2 = np.abs(z) <= 3.5
    rr = rr[mask2]

    return rr.tolist()
