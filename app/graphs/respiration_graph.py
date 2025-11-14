# app/graphs/respiration_graph.py
# --------------------------------
# Graphe de respiration guidée + respiration réelle (EDR)

import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class RespirationGraph(QWidget):
    """
    Affiche :
    - la respiration guidée (sinus, triangle…)
    - la respiration estimée (EDR)
    - un point mobile indiquant la phase actuelle
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # ---------- Matplotlib ----------
        self.fig = Figure(figsize=(5, 3), dpi=90)
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.ax = self.fig.add_subplot(111)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self._setup_style()

        # courbes
        self.line_guide = None
        self.line_edr = None
        self.dot = None

    # ------------------------------------------------------------
    def _setup_style(self):
        """Style doux personnalisé."""
        self.ax.set_facecolor("#f2f2f2")
        self.fig.patch.set_facecolor("#f2f2f2")

        self.ax.grid(True, alpha=0.25, color="#999999")
        self.ax.set_title("Respiration", fontsize=11)
        self.ax.set_ylim(-1.2, 1.2)
        self.ax.set_xlim(-20, 0)
        self.ax.set_xlabel("Temps (s)")
        self.ax.set_ylabel("Amplitude")

    # ------------------------------------------------------------
    def update(self, guide_curve, edr_curve=None, dot_value=None):
        """
        guide_curve : (t, y)
        edr_curve   : (t, y) ou None
        dot_value   : float entre -1 et +1 (position du point) ou None
        """

        if guide_curve is None:
            return

        t_guide, y_guide = guide_curve

        # --------- guide ---------
        if self.line_guide is None:
            (self.line_guide,) = self.ax.plot(
                t_guide, y_guide,
                color="#008800",
                linewidth=2.0,
                label="Guide"
            )
        else:
            self.line_guide.set_data(t_guide, y_guide)

        # --------- EDR ---------
        if edr_curve:
            t_edr, y_edr = edr_curve

            if self.line_edr is None:
                (self.line_edr,) = self.ax.plot(
                    t_edr, y_edr,
                    color="#0055cc",
                    linewidth=1.4,
                    alpha=0.7,
                    label="Resp. réelle"
                )
            else:
                self.line_edr.set_data(t_edr, y_edr)

        # --------- moving dot ---------
        if dot_value is not None:
            if self.dot is None:
                (self.dot,) = self.ax.plot(
                    [0], [dot_value],
                    "o", color="red", markersize=8
                )
            else:
                self.dot.set_data([0], [dot_value])

        # --------- redraw ---------
        self.ax.set_xlim(-20, 0)
        self.canvas.draw()
