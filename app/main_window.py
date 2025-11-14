# app/main_window.py

import numpy as np
from PySide6 import QtCore, QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from pipeline.processor import Processor
from ble.ble_worker import BLEWorker
from resp_guide.guide import RespGuideGenerator


# ----------------------------------------------------------------------
# Petit wrapper Matplotlib
# ----------------------------------------------------------------------
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, width=5, height=2, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)


# ----------------------------------------------------------------------
# FENÊTRE PRINCIPALE
# ----------------------------------------------------------------------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cohérence Cardiaque – V3 Stable")
        self.resize(1280, 720)

        # === HRV Processor ===
        self.processor = Processor()

        # === Respiration guidée ===
        self.resp_guide = RespGuideGenerator()

        # === BLE (simulation RR) ===
        self.ble = BLEWorker()
        self.ble.new_rr_signal.connect(self.on_new_rr)
        self.ble.status_signal.connect(self.on_ble_status)

        # === UI ===
        self.build_ui()

        # === Timer UI ===
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.refresh_ui)
        self.timer.start(250)  # 5 Hz

        # === Lancer simulation BLE ===
        self.ble.start()

    # ------------------------------------------------------------------
    # RÉCEPTION RR BLE
    # ------------------------------------------------------------------
    def on_new_rr(self, rr_value: int):
        self.processor.push_rr(rr_value)

    def on_ble_status(self, txt: str):
        self.label_ble.setText(f"BLE : {txt}")

    # ------------------------------------------------------------------
    # Interface principale
    # ------------------------------------------------------------------
    def build_ui(self):
        central = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        self.setCentralWidget(central)

        # =============================
        # Colonne GAUCHE (graphes)
        # =============================
        left = QtWidgets.QVBoxLayout()
        left.setSpacing(20)

        # --------- RR graph ------------
        box_rr = QtWidgets.QGroupBox("RR (ms)")
        box_rr_layout = QtWidgets.QVBoxLayout(box_rr)

        self.can_rr = MplCanvas(width=6, height=2.3, dpi=100)
        self.ax_rr = self.can_rr.fig.add_subplot(111)
        self.ax_rr.grid(alpha=0.3)
        self.line_rr, = self.ax_rr.plot([], [], lw=1.6)

        box_rr_layout.addWidget(self.can_rr)
        left.addWidget(box_rr)

        # --------- Spectre HRV ----------
        box_spec = QtWidgets.QGroupBox("Spectre HRV")
        box_spec_layout = QtWidgets.QVBoxLayout(box_spec)

        self.can_spec = MplCanvas(width=6, height=2.3, dpi=100)
        self.ax_spec = self.can_spec.fig.add_subplot(111)
        self.ax_spec.grid(alpha=0.3)
        self.line_spec, = self.ax_spec.plot([], [], lw=1.6)

        box_spec_layout.addWidget(self.can_spec)
        left.addWidget(box_spec)

        # --------- Respiration ----------
        box_resp = QtWidgets.QGroupBox("Respiration")
        box_resp_layout = QtWidgets.QVBoxLayout(box_resp)

        self.can_resp = MplCanvas(width=6, height=2.3, dpi=100)
        self.ax_resp = self.can_resp.fig.add_subplot(111)
        self.ax_resp.grid(alpha=0.3)

        # Resp. guidée (vert)
        self.line_resp, = self.ax_resp.plot([], [], lw=1.8, color="green")

        # Resp estimée (orange)
        self.line_resp_est, = self.ax_resp.plot([], [], lw=1.5, color="orange")

        box_resp_layout.addWidget(self.can_resp)
        left.addWidget(box_resp)

        layout.addLayout(left, stretch=3)

        # =============================
        # Colonne DROITE (infos)
        # =============================
        right = QtWidgets.QVBoxLayout()
        right.setSpacing(20)

        # --------- BLE Status ----------
        box_ble = QtWidgets.QGroupBox("BLE")
        ble_layout = QtWidgets.QVBoxLayout(box_ble)

        self.label_ble = QtWidgets.QLabel("BLE : …")
        self.label_ble.setStyleSheet("font-weight:bold; font-size:13px;")

        ble_layout.addWidget(self.label_ble)
        right.addWidget(box_ble)

        # --------- Sliders respiration ----------
        box_sliders = QtWidgets.QGroupBox("Respiration guidée")
        sliders_layout = QtWidgets.QVBoxLayout(box_sliders)

        lbl_i = QtWidgets.QLabel("Inspiration (s)")
        self.sl_insp = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.sl_insp.setRange(3, 8)
        self.sl_insp.setValue(4)

        lbl_e = QtWidgets.QLabel("Expiration (s)")
        self.sl_exp = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.sl_exp.setRange(3, 12)
        self.sl_exp.setValue(6)

        sliders_layout.addWidget(lbl_i)
        sliders_layout.addWidget(self.sl_insp)
        sliders_layout.addWidget(lbl_e)
        sliders_layout.addWidget(self.sl_exp)

        right.addWidget(box_sliders)

        # --------- Stats HRV ----------
        box_stats = QtWidgets.QGroupBox("Indicateurs HRV")
        stats_layout = QtWidgets.QVBoxLayout(box_stats)

        self.lbl_rmssd = QtWidgets.QLabel("RMSSD : 0.0")
        self.lbl_lf = QtWidgets.QLabel("LF : 0.000")
        self.lbl_hf = QtWidgets.QLabel("HF : 0.000")
        self.lbl_ratio = QtWidgets.QLabel("LF/HF : 0.000")
        self.lbl_resp = QtWidgets.QLabel("Resp (Hz) : 0.000")
        self.lbl_score = QtWidgets.QLabel("Score : 0.0")

        for w in [self.lbl_rmssd, self.lbl_lf, self.lbl_hf,
                  self.lbl_ratio, self.lbl_resp, self.lbl_score]:
            w.setStyleSheet("font-size:13px;")
            stats_layout.addWidget(w)

        right.addWidget(box_stats)

        # Push right layout
        layout.addLayout(right, stretch=1)

    # ------------------------------------------------------------------
    # Mise à jour du graphique de respiration guidée
    # ------------------------------------------------------------------
    def update_resp_guided_plot(self, t, y):
        """Mise à jour de la courbe de respiration guidée (verte)."""

        self.line_resp.set_data(t, y)

        if len(t) > 1:
            # Fixe X de 0 → durée totale
            self.ax_resp.set_xlim(0, t[-1])

            # Fixe Y pour garder un affichage stable
            self.ax_resp.set_ylim(-1.1, 1.1)

        self.can_resp.draw()

    # ------------------------------------------------------------------
    # Rafraîchissement UI
    # ------------------------------------------------------------------
    def refresh_ui(self):
        # ------------------------------------------------------------
        # 1) Avance la respiration guidée (phase interne)
        # ------------------------------------------------------------
        self.resp_guide.step()

        # ------------------------------------------------------------
        # 2) Lire les sliders et mettre à jour les durées
        # ------------------------------------------------------------
        insp = self.sl_insp.value()
        exp = self.sl_exp.value()
        self.resp_guide.set_durations(insp, exp)

        # ------------------------------------------------------------
        # 3) Générer l’onde respiration guidée (premium cohérence 365)
        # ------------------------------------------------------------
        t, y = self.resp_guide.generate_waveform()
        self.update_resp_guided_plot(t, y)

        # ------------------------------------------------------------
        # 4) Calcul HRV complet (RR + spectre + score + EDR)
        # ------------------------------------------------------------
        state = self.processor.compute_state()

        # ------------------------------------------------------------
        # 5) Mise à jour du graphe RR
        # ------------------------------------------------------------
        if len(state.rr_list) > 2:
            x = np.arange(len(state.rr_list))
            self.line_rr.set_data(x, state.rr_list)

            self.ax_rr.set_xlim(0, len(state.rr_list))
            self.ax_rr.set_ylim(min(state.rr_list) - 50,
                                max(state.rr_list) + 50)
            self.can_rr.draw()

        # ------------------------------------------------------------
        # 6) Mise à jour spectre (power vs freq)
        # ------------------------------------------------------------
        if len(state.freq) > 2:
            self.line_spec.set_data(state.freq, state.power)

            self.ax_spec.set_xlim(0, 0.5)
            self.ax_spec.set_ylim(0, max(state.power) * 1.1)
            self.can_spec.draw()

        # ------------------------------------------------------------
        # 7) Mise à jour respiration estimée (EDR / RSA)
        # ------------------------------------------------------------
        if state.resp_signal is not None and len(state.resp_signal) > 2:
            self.line_resp_est.set_data(state.resp_time, state.resp_signal)

            self.ax_resp.set_xlim(0, max(state.resp_time))
            self.ax_resp.set_ylim(min(state.resp_signal),
                                  max(state.resp_signal))
            self.can_resp.draw()

        # ------------------------------------------------------------
        # 8) Mise à jour des labels HRV
        # ------------------------------------------------------------
        self.lbl_rmssd.setText(f"{state.rmssd:.1f}")
        self.lbl_lf.setText(f"{state.lf:.3f}")
        self.lbl_hf.setText(f"{state.hf:.3f}")
        self.lbl_ratio.setText(f"{state.lf_hf_ratio:.3f}")
        self.lbl_resp.setText(f"{state.resp_freq:.3f}")
        self.lbl_score.setText(f"{state.score:.1f}")
