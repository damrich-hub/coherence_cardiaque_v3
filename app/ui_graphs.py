# app/ui_graphs.py
"""
ui_graphs.py
------------
Widgets d'affichage graphiques (Matplotlib).

Pour l’instant :
- RespirationGraph : graphe de respiration guidée (et plus tard réelle).
"""

from typing import Sequence

import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class RespirationGraph(QWidget):
    """
    Graphe de respiration guidée (et éventuellement réelle plus tard).
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.figure = Figure(figsize=(6, 3))
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)

        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Respiration guidée")
        self.ax.set_xlabel("Temps (s)")
        self.ax.set_ylabel("Amplitude")
        self.ax.set_ylim(-1.1, 1.1)

        (self.line_guide,) = self.ax.plot([], [], color="green", label="Guidée")
        self.ax.legend(loc="upper right")

    def plot_guided_resp(self, t: Sequence[float], y: Sequence[float]):
        """
        Met à jour la courbe de respiration guidée.
        """
        t = np.asarray(t, float)
        y = np.asarray(y, float)

        self.line_guide.set_data(t, y)

        if t.size > 0:
            self.ax.set_xlim(float(t.min()), float(t.max()))

        self.canvas.draw()
