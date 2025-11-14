"""
Module core
-----------
Utilitaires transverses utilisés par toute l'application :
- circular_buffer : buffers circulaires thread-safe (RR, LF/HF, etc.)
- time_utils      : horloges, conversions ms/s, helpers temporels
- math_utils      : clamp, safe_float, moyenne glissante, etc.
- smoothing       : EMA, lissage, anti-sauts, rate limiter
- debug           : logger prêt à l'emploi, décorateurs d'aide au debug
"""
from .math_utils import clamp, safe_float

def safe_float(x, fallback=0.0) -> float:
    """
    Convertit en float en gérant les erreurs et valeurs non valides.
    Exemple : safe_float("nan") → 0.0
    """
    try:
        v = float(x)
        if math.isnan(v) or math.isinf(v):
            return fallback
        return v
    except Exception:
        return fallback
