"""
Module edr (Estimation de la Respiration)
-----------------------------------------
Contient toutes les méthodes d'extraction du signal respiratoire à partir
des intervalles RR :

- edr_basic.py   : Estimations simples (Welch, sinus repère).
- edr_premium.py : Méthode avancée RSA + filtre + autocorr + EMA.
- respiration_edr.py : Backend EDR utilisant NeuroKit2 (filtrage / detrend).
- fusion.py      : Combinaison pondérée des estimateurs.
- helpers.py     : Fonctions utilitaires (interpolation, filtrage, normalisation).

Le but de ce module est de centraliser toute la logique respiratoire afin
que l'interface (UI) et le BLE restent indépendants et légers.
"""

from .edr_basic import estimate_cpm_welch, generate_sinus
from .edr_premium import EDRPremium
from .respiration_edr import extract_respiration_edr
from .fusion import fuse_estimates
from .helpers import (
    interpolate_rr,
    compute_rsa,
    normalize_signal,
    EDR_FS,
)

__all__ = [
    "estimate_cpm_welch",
    "generate_sinus",
    "EDRPremium",
    "extract_respiration_edr",
    "fuse_estimates",
    "interpolate_rr",
    "compute_rsa",
    "normalize_signal",
    "EDR_FS",
]
