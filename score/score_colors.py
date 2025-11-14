# -*- coding: utf-8 -*-
"""
score/score_colors.py
---------------------
Gestion des couleurs d'affichage selon les plages de qualité.
"""

def color_for_value(metric: str, value: float) -> str:
    """Retourne une couleur hex selon la métrique et sa valeur."""
    if metric == "SDNN":
        if value < 30: return "#f8cccc"
        if value < 60: return "#ffe7b3"
        return "#c7f5c1"
    elif metric == "RMSSD":
        if value < 25: return "#f8cccc"
        if value < 50: return "#ffe7b3"
        return "#c7f5c1"
    elif metric == "LFHF":
        if value < 0.5 or value > 3.0: return "#f8cccc"
        if 0.5 <= value < 1.5 or 2.0 < value <= 3.0: return "#ffe7b3"
        return "#c7f5c1"
    elif metric == "SCORE":
        if value < 40: return "#f8cccc"
        if value < 70: return "#ffe7b3"
        return "#c7f5c1"
    return "#fafafa"
