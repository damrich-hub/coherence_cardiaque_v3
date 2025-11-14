# hrv/utils.py
"""
Utilitaires généraux pour le traitement HRV.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np


def detrend_signal(x: Iterable[float]) -> np.ndarray:
    """
    Supprime la tendance linéaire d'un signal RR interpolé.

    Parameters
    ----------
    x : Iterable[float]

    Returns
    -------
    np.ndarray
        Signal détrendé.
    """
    x_arr = np.asarray(list(x), dtype=float)
    if x_arr.size < 3:
        return x_arr

    t = np.arange(x_arr.size)
    # Fit linéaire y = a t + b
    a, b = np.polyfit(t, x_arr, 1)

    trend = a * t + b
    return x_arr - trend


def normalize_signal(x: Iterable[float]) -> np.ndarray:
    """
    Normalise un signal entre 0 et 1.

    Parameters
    ----------
    x : Iterable[float]

    Returns
    -------
    np.ndarray
        Signal normalisé dans [0, 1].
    """
    x_arr = np.asarray(list(x), dtype=float)
    if x_arr.size == 0:
        return x_arr

    xmin = float(x_arr.min())
    xmax = float(x_arr.max())
    if xmax - xmin < 1e-12:
        return np.zeros_like(x_arr)

    return (x_arr - xmin) / (xmax - xmin)
