# resp_guide/guide.py

import numpy as np


class RespGuideGenerator:
    """
    Génère une respiration guidée sinusoïdale
    avec une phase interne qui avance au cours du temps.
    """

    def __init__(self, insp=4, exp=6):
        self.insp = insp
        self.exp = exp
        self.phase = 0.0      # secondes
        self.dt = 0.05        # pas de temps pour step() ~ 20 Hz

    def set_durations(self, insp, exp):
        self.insp = max(1, float(insp))
        self.exp = max(1, float(exp))

    def step(self):
        """Avance d'un pas de temps pour animer la respiration."""
        self.phase += self.dt
        T = self.insp + self.exp
        if T <= 0:
            T = 1.0
        self.phase = self.phase % T

    def generate_waveform(self, duration=10.0):
        """
        Retourne (t, y) pour tracer la respiration guidée.
        y va de -1 à +1 environ.
        """
        T = self.insp + self.exp
        if T <= 0:
            T = 1.0

        t = np.linspace(0, duration, 400)
        y = np.sin(2 * np.pi * (t + self.phase) / T)

        return t, y
