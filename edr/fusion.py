"""
fusion.py
---------
Fusion de plusieurs estimateurs EDR :
- Welch (spectral)
- RSA / méthodes avancées
- pondération par confiance (0..1)
"""

from .helpers import EDR_FS, normalize_signal  # EDR_FS pas utilisé ici mais centralisé


def fuse_estimates(values, weights):
    """
    Fusionne des estimations respiratoires (en cpm) en utilisant une moyenne pondérée.

    Parameters
    ----------
    values : list[float]
        Liste de valeurs de fréquence respiratoire (cpm).
    weights : list[float]
        Poids associés (0..1).

    Returns
    -------
    cpm_fused : float ou None
        Fréquence fusionnée en cpm.
    """
    if not values:
        return None

    if len(values) == 1:
        return float(values[0])

    w = [max(0.0, float(x)) for x in weights]
    s = sum(w)
    if s == 0:
        return float(values[0])

    return float(sum(v * wt for v, wt in zip(values, w)) / s)
