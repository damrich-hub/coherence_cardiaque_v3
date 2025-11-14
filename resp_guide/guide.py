import numpy as np


class RespGuide:
    """
    Classe basique contenant la logique de génération
    d'une courbe de respiration.
    """

    def __init__(self, insp_duration=4, exp_duration=6):
        self.insp = insp_duration
        self.exp = exp_duration

    def set_durations(self, insp, exp):
        self.insp = insp
        self.exp = exp

    def generate_waveform(self):
        """
        Génère une courbe d'inspiration/expiration simple.
        Retourne :
            - t : temps
            - y : amplitude normalisée
        """
        T = self.insp + self.exp
        t = np.linspace(0, T, 300)

        y = np.zeros_like(t)
        for i, ti in enumerate(t):
            if ti < self.insp:
                # phase inhalation
                y[i] = ti / self.insp
            else:
                # phase exhalation (cosine douce)
                x = (ti - self.insp) / self.exp
                y[i] = np.cos(x * np.pi)

        return t, y


class RespGuideGenerator:
    """
    Wrapper compatible avec l'ancien code MainWindow.
    Expose une méthode generate_wave() appelée par la fenêtre.
    """

    def __init__(self, insp=4, exp=6):
        self.guide = RespGuide(insp_duration=insp, exp_duration=exp)

    def set_durations(self, insp, exp):
        self.guide.set_durations(insp, exp)

    def generate_wave(self):
        """
        Méthode attendue par MainWindow.
        Simple wrapper vers generate_waveform().
        """
        return self.guide.generate_waveform()
