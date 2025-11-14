import numpy as np


class RespGuideGenerator:
    """
    Génère une respiration guidée basée sur un cycle inspi/expi
    avec montée sur 'insp_duration' secondes et descente sur
    'exp_duration' secondes, parfaitement synchronisée.
    """

    def __init__(self, insp_duration=4.0, exp_duration=6.0):
        self.insp = insp_duration
        self.exp = exp_duration
        self.phase = 0.0     # phase dans le cycle (secondes)
        self.dt = 0.2        # pas de temps nominal (lié au refresh)

    # -------------------------------------------------------
    def set_durations(self, insp, exp):
        """Met à jour les durées du cycle."""
        self.insp = max(0.5, float(insp))
        self.exp = max(0.5, float(exp))

    # -------------------------------------------------------
    def step(self):
        """Avance la phase d'un pas de dt, en boucle."""
        total = self.insp + self.exp
        self.phase = (self.phase + self.dt) % total

    # -------------------------------------------------------
    def generate_waveform(self):
        """
        Génère la courbe complète d'un cycle pour l'affichage :
        - montée linéaire ou sinusoïdale sur phase inspi
        - descente sur phase expi
        """
        total = self.insp + self.exp

        # 100 points par cycle → propre pour l'affichage
        t = np.linspace(0, total, 200)

        y = np.zeros_like(t)

        # Inspir : 0 → +1
        mask_insp = t < self.insp
        x_insp = t[mask_insp] / self.insp
        y[mask_insp] = np.sin(x_insp * np.pi / 2)   # montée douce

        # Expi : +1 → -1
        mask_exp = t >= self.insp
        x_exp = (t[mask_exp] - self.insp) / self.exp
        y[mask_exp] = np.cos(x_exp * np.pi)         # descend de +1 à -1

        return t, y

    # -------------------------------------------------------
    def get_instant_value(self):
        """
        Donne la valeur Y instantanée de la respiration guidée,
        utile si tu veux synchroniser un point mobile.
        """
        if self.phase < self.insp:
            x = self.phase / self.insp
            return np.sin(x * np.pi / 2)
        else:
            x = (self.phase - self.insp) / self.exp
            return np.cos(x * np.pi)

