# -*- coding: utf-8 -*-
"""
core/math_utils.py
-------------------
Fonctions mathématiques utilitaires pour l’analyse HRV, EDR et Score.

Ce module regroupe les outils mathématiques génériques :
- Sécurité numérique (safe_float)
- Clamp / Normalisation
- Moyennes glissantes
- Interpolation uniforme
- Statistiques simples (RMS, z-score)
"""

import math
import numpy as np
from scipy.interpolate import interp1d


# ---------------------------------------------------------------------
# Sécurité numérique
# ---------------------------------------------------------------------
def safe_float(x, fallback=0.0) -> float:
    """
    Convertit en float en gérant les erreurs et valeurs non valides.
    Exemple :
        safe_float("nan") -> 0.0
        safe_float("123") -> 123.0
    """
    try:
        v = float(x)
        if math.isnan(v) or math.isinf(v):
            return fallback
        return v
    except Exception:
        return fallback


# ---------------------------------------------------------------------
# Bornage / Normalisation
# ---------------------------------------------------------------------
def clamp(value: float, vmin: float, vmax: float) -> float:
    """
    Contraint une valeur dans un intervalle donné.
    Exemple : clamp(110, 0, 100) -> 100
    """
    return max(vmin, min(vmax, value))


def normalize(value: float, vmin: float, vmax: float) -> float:
    """
    Normalise une valeur entre 0 et 1 dans un intervalle [vmin, vmax].
    Si vmin == vmax, retourne 0.5.
    """
    if vmax == vmin:
        return 0.5
    return (value - vmin) / (vmax - vmin)


def normalize_range(value: float, vmin: float, vmax: float,
                    out_min: float, out_max: float) -> float:
    """
    Normalise une valeur dans un intervalle [out_min, out_max].
    """
    n = normalize(value, vmin, vmax)
    return out_min + n * (out_max - out_min)


# ---------------------------------------------------------------------
# Lissage et moyennes glissantes
# ---------------------------------------------------------------------
def moving_average(x: np.ndarray, window: int = 5) -> np.ndarray:
    """
    Moyenne glissante centrée (fenêtre mobile).
    """
    if window <= 1 or len(x) < window:
        return np.asarray(x)
    kernel = np.ones(window) / window
    return np.convolve(x, kernel, mode="valid")


def exponential_smoothing(x: np.ndarray, alpha: float = 0.2) -> np.ndarray:
    """
    Lissage exponentiel simple.
    alpha ∈ [0,1] : plus alpha est grand, plus la réactivité est forte.
    """
    if len(x) == 0:
        return np.array([])
    s = np.zeros_like(x, dtype=float)
    s[0] = x[0]
    for i in range(1, len(x)):
        s[i] = alpha * x[i] + (1 - alpha) * s[i - 1]
    return s


# ---------------------------------------------------------------------
# Interpolation et rééchantillonnage
# ---------------------------------------------------------------------
def interpolate_uniform(x: np.ndarray, y: np.ndarray, fs: float = 4.0) -> tuple[np.ndarray, np.ndarray]:
    """
    Interpole une série irrégulière (x, y) en signal uniforme.
    Exemple : utile pour RR → interpolation à 4 Hz pour analyse spectrale.
    """
    if len(x) < 2:
        return x, y
    x_uniform = np.arange(x[0], x[-1], 1 / fs)
    f = interp1d(x, y, kind="linear", fill_value="extrapolate")
    y_uniform = f(x_uniform)
    return x_uniform, y_uniform


# ---------------------------------------------------------------------
# Autres fonctions pratiques
# ---------------------------------------------------------------------
def rms(x: np.ndarray) -> float:
    """
    Calcule la racine carrée de la moyenne des carrés.
    """
    if len(x) == 0:
        return 0.0
    return float(np.sqrt(np.mean(x ** 2)))


def z_score(x: np.ndarray) -> np.ndarray:
    """
    Standardise un vecteur : moyenne 0, écart-type 1.
    """
    if len(x) < 2:
        return np.zeros_like(x)
    return (x - np.mean(x)) / np.std(x)


# ---------------------------------------------------------------------
# Test local
# ---------------------------------------------------------------------
if __name__ == "__main__":
    arr = np.array([1, 2, 3, 4, 5])
    print("Clamp(120,0,100):", clamp(120, 0, 100))
    print("Safe float('nan'):", safe_float("nan"))
    print("Normalize(7,0,10):", normalize(7, 0, 10))
    print("Moving average:", moving_average(arr, 3))
    print("Exp smoothing:", exponential_smoothing(arr, 0.3))
    print("RMS:", rms(arr))
