# app/graphs/rr_graph.py

from collections import deque
from typing import Sequence, Optional

import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

# Fenêtre de temps (en secondes) pour l'affichage RR
RR_WINDOW_SEC = 120.0
# Bornes de RR raisonnables
MIN_RR_MS = 300.0
MAX_RR_MS = 2000.0
# Lissage visuel
EMA_VISUAL_RR = 0.6


def _moving_average_like(rr: np.ndarray, win: int = 7) -> np.ndarray:
    """
    Lissage simple façon "sinusoïde" pour lisser un peu les RR.
    """
    if rr.size <= 2:
        return rr.copy()

    w = max(3, int(win) | 1)  # fenêtre impaire
    pad = w // 2
    pad_rr = np.pad(rr, (pad, pad), mode="edge")
    k = np.ones(w) / w
    return np.convolve(pad_rr, k, mode="valid")


class RRGraph(QWidget):
    """
    Graphe des intervalles RR (ms) dans le temps.

    API principale :
        update(rr_ts, rr_ms)

        - rr_ts : liste de timestamps (en secondes, type float)
        - rr_ms : liste de RR (ms)
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
        self.ax.set_title("RR (ms)")
        self.ax.set_xlabel("Temps (s)")
        self.ax.set_ylabel("RR (ms)")
        self.ax.grid(True, alpha=0.3)

        # Style doux
        self._fig.patch.set_facecolor("#f7f7f7")
        self.ax.set_facecolor("#ffffff")

        (self.line_rr,) = self.ax.plot([], [], lw=1.4, color="#2f7ed8")

        self._last_vis_rr: Optional[float] = None

        # Historique interne (optionnel, si on veut l'utiliser plus tard)
        self._rr_ts_hist: deque[float] = deque(maxlen=4000)
        self._rr_ms_hist: deque[float] = deque(maxlen=4000)

    # ------------------------------------------------------------------ #
    def update(self, rr_ts: Sequence[float], rr_ms: Sequence[float]) -> None:
        """
        Met à jour le graphe RR.

        On suppose :
            len(rr_ts) == len(rr_ms)
        et rr_ts en secondes croissants.
        """
        if not rr_ts or not rr_ms or len(rr_ts) != len(rr_ms):
            # rien à tracer
            self.line_rr.set_data([], [])
            self._canvas.draw_idle()
            return

        ts = np.asarray(rr_ts, dtype=float)
        rr = np.asarray(rr_ms, dtype=float)

        # Clamp grossier
        rr = np.clip(rr, MIN_RR_MS, MAX_RR_MS)

        # Lissage
        rr_smooth = _moving_average_like(rr, win=7)

        # EMA sur le dernier point pour éviter les sauts
        if self._last_vis_rr is None:
            vis = rr_smooth.copy()
            self._last_vis_rr = float(vis[-1])
        else:
            vis = rr_smooth.copy()
            vis[-1] = (
                EMA_VISUAL_RR * rr_smooth[-1] + (1.0 - EMA_VISUAL_RR) * self._last_vis_rr
            )
            self._last_vis_rr = float(vis[-1])

        # Fenêtre glissante
        t_max = float(ts[-1])
        t_min = max(ts[0], t_max - RR_WINDOW_SEC)

        mask = ts >= t_min
        ts_win = ts[mask] - t_min  # on remet à zéro pour l'affichage
        rr_win = vis[mask]

        self.line_rr.set_data(ts_win, rr_win)

        # X : 0 -> RR_WINDOW_SEC
        xmax = max(5.0, ts_win[-1]) if ts_win.size > 0 else RR_WINDOW_SEC
        self.ax.set_xlim(0.0, max(10.0, min(xmax + 1.0, RR_WINDOW_SEC)))

        # Y auto, mais borné
        if rr_win.size > 0:
            ymin = float(np.min(rr_win)) - 60.0
            ymax = float(np.max(rr_win)) + 60.0
            ymin = max(MIN_RR_MS, ymin)
            ymax = min(MAX_RR_MS, ymax)
            if ymax - ymin < 200.0:
                ymax = ymin + 200.0
            self.ax.set_ylim(ymin, ymax)

        self._canvas.draw_idle()
