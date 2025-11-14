import numpy as np

class RespGuide:
    """
    Génère une onde "respiration guidée" de type sinus,
    avec durées inspiration / expiration ajustables.
    """
    def __init__(self, insp_duration=4.0, exp_duration=6.0):
        self.insp_duration = float(insp_duration)
        self.exp_duration = float(exp_duration)

    def set_durations(self, insp, exp):
        self.insp_duration = float(insp)
        self.exp_duration = float(exp)

    def generate_waveform(self, n_points=300):
        """
        Renvoie une onde sinus modélisant un cycle inspi + expi.
        """
        T = self.insp_duration + self.exp_duration
        t = np.linspace(0, T, n_points)

        # Inspiration : 0 -> pi
        # Expiration : pi -> 2pi (plus longue possible)
        ratio = self.insp_duration / T
        split = int(n_points * ratio)

        y = np.zeros_like(t)

        # phase inspiration
        y[:split] = np.sin(np.linspace(0, np.pi, split))

        # phase expiration
        y[split:] = np.sin(np.linspace(np.pi, 2 * np.pi, n_points - split))

        return t, y


class RespGuideGenerator:
    """
    Wrapper pour compatibilité avec l'ancien code (MainWindow).
    """
    def __init__(self, insp=4.0, exp=6.0):
        self.guide = RespGuide(insp_duration=insp, exp_duration=exp)

    def set_durations(self, insp, exp):
        self.guide.set_durations(insp, exp)

    def set_times(self, insp, exp):
        """Alias pour compatibilité avec l’ancien code."""
        self.set_durations(insp, exp)

    def generate_wave(self):
        """Méthode attendue par MainWindow."""
        return self.guide.generate_waveform()
