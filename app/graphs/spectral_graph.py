# app/graphs/spectral_graph.py

from collections import deque
from typing import Optional

import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


SPECTRAL_WINDOW_POINTS = 120  # nombre de points gardés en historique
MIN_Y_MAX = 200.0             # hauteur minimale du graphe


class SpectralGraph(QWidget):
    """
    Graphe spectral simplifié :
    - courbe LF
    - courbe HF
    - courbe du ratio LF/HF (pointillés)

    API :
        update(lf, hf, ratio)

    On lui passe les valeurs « instantanées » ou lissées ;
    le widget maintient sa propre historique.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Canvas Matplotlib
        self._fig = Figure(figsize=(6, 2.6), dpi=100)
        self._canvas = FigureCanvasQTAgg(self._fig)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._canvas)

        self.ax = self._fig.add_subplot(111)
        self.ax.set_title("Spectral LF / HF")
        self.ax.set_xlabel("Temps (points)")
        self.ax.set_ylabel("Puissance (a.u.)")
        self.ax.grid(True, alpha=0.3)

        # Style doux
        self._fig.patch.set_facecolor("#f7f7f7")
        self.ax.set_facecolor("#ffffff")

        (self.line_lf,) = self.ax.plot([], [], lw=1.4, label="LF", color="#2f7ed8")
        (self.line_hf,) = self.ax.plot([], [], lw=1.4, label="HF", color="#8bbc21")
        (self.line_ratio,) = self.ax.plot(
            [], [], lw=1.2, linestyle="--", label="LF/HF", color="#910000"
        )

        self.ax.legend(loc="upper left")

        # Historiques
        self._lf_hist: deque[float] = deque(maxlen=SPECTRAL_WINDOW_POINTS)
        self._hf_hist: deque[float] = deque(maxlen=SPECTRAL_WINDOW_POINTS)
        self._ratio_hist: deque[float] = deque(maxlen=SPECTRAL_WINDOW_POINTS)

        self._ymax_ema: Optional[float] = None

    # ------------------------------------------------------------------ #
    def update(self, lf: float, hf: float, ratio: float) -> None:
        """
        Ajoute un nouveau point et met à jour le graphe.
        """
        self._lf_hist.append(float(max(lf, 0.0)))
        self._hf_hist.append(float(max(hf, 0.0)))
        self._ratio_hist.append(float(max(ratio, 0.0)))

        if not self._lf_hist:
            self.line_lf.set_data([], [])
            self.line_hf.set_data([], [])
            self.line_ratio.set_data([], [])
            self._canvas.draw_idle()
            return

        # Axe X = index des points
        x = np.arange(len(self._lf_hist))
        lf_arr = np.asarray(self._lf_hist)
        hf_arr = np.asarray(self._hf_hist)
        ratio_arr = np.asarray(self._ratio_hist)

        self.line_lf.set_data(x, lf_arr)
        self.line_hf.set_data(x, hf_arr)
        self.line_ratio.set_data(x, ratio_arr)

        # X : fenêtre glissante
        x_max = float(x[-1])
        x_min = max(0.0, x_max - SPECTRAL_WINDOW_POINTS + 1)
        self.ax.set_xlim(x_min, x_max + 1.0)

        # Y : dynamique + lissage EMA
        current_max = float(
            max(
                MIN_Y_MAX,
                float(np.max(lf_arr)),
                float(np.max(hf_arr)),
            )
        )
        target_ymax = current_max * 1.2

        if self._ymax_ema is None:
            self._ymax_ema = target_ymax
        else:
            self._ymax_ema = 0.85 * self._ymax_ema + 0.15 * target_ymax

        self.ax.set_ylim(0.0, max(MIN_Y_MAX, self._ymax_ema))

        self._canvas.draw_idle()
