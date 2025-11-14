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
        self.timer.start(200)  # 5 Hz

        # === Lancer simulation BLE ===
        self.ble.start()

    # ------------------------------------------------------------------
    # RÉCEPTION RR BLE
    # ------------------------------------------------------------------
    def on_new_rr(self, rr_value: int):
        self.processor.push_rr(rr_value)

    def on_ble_status(self, txt: str):
        self.lbl_ble.setText(f"BLE : {txt}")

    # ------------------------------------------------------------------
    # Interface principale
    # ------------------------------------------------------------------
    def build_ui(self):
        central = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(central)
        self.setCentralWidget(central)

        # --------------------------------------------------------------
        # COLONNE GAUCHE (3 graphes)
        # --------------------------------------------------------------
        left = QtWidgets.QVBoxLayout()

        # === Graphe RR ===
        self.can_rr = MplCanvas()
        self.ax_rr = self.can_rr.fig.add_subplot(111)
        self.ax_rr.set_title("RR (ms)")
        self.ax_rr.grid(True, alpha=0.3)
        self.line_rr, = self.ax_rr.plot([], [], lw=1.4)
        left.addWidget(self.can_rr)

        # === Spectre HRV ===
        self.can_spec = MplCanvas()
        self.ax_spec = self.can_spec.fig.add_subplot(111)
        self.ax_spec.set_title("Spectre HRV")
        self.ax_spec.grid(True, alpha=0.3)
        self.line_spec, = self.ax_spec.plot([], [], lw=1.4)
        left.addWidget(self.can_spec)

        # === Respiration guidée + estimée ===
        self.can_resp = MplCanvas()
        self.ax_resp = self.can_resp.fig.add_subplot(111)
        self.ax_resp.set_title("Respiration")
        self.ax_resp.grid(True, alpha=0.3)

        # Courbe verte (resp guidée)
        self.line_resp, = self.ax_resp.plot([], [], lw=1.8, color="green")
        # Courbe orange (resp estimée)
        self.line_resp_est, = self.ax_resp.plot([], [], lw=1.5, color="orange")

        left.addWidget(self.can_resp)

        layout.addLayout(left)

        # --------------------------------------------------------------
        # COLONNE DROITE (sliders + infos)
        # --------------------------------------------------------------
        right = QtWidgets.QVBoxLayout()

        # === BLE status ===
        self.lbl_ble = QtWidgets.QLabel("BLE : —")
        font = self.lbl_ble.font()
        font.setPointSize(11)
        font.setBold(True)
        self.lbl_ble.setFont(font)
        right.addWidget(self.lbl_ble)

        # === Sliders respiration guidée ===
        right.addWidget(QtWidgets.QLabel("Respiration guidée"))

        self.sl_insp = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.sl_insp.setMinimum(2)
        self.sl_insp.setMaximum(10)
        self.sl_insp.setValue(4)
        right.addWidget(QtWidgets.QLabel("Inspiration (s)"))
        right.addWidget(self.sl_insp)

        self.sl_exp = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.sl_exp.setMinimum(2)
        self.sl_exp.setMaximum(12)
        self.sl_exp.setValue(6)
        right.addWidget(QtWidgets.QLabel("Expiration (s)"))
        right.addWidget(self.sl_exp)

        # === HRV Infos ===
        right.addWidget(QtWidgets.QLabel("Indicateurs HRV"))

        self.lbl_rmssd = QtWidgets.QLabel("RMSSD : 0")
        self.lbl_lf = QtWidgets.QLabel("LF : 0")
        self.lbl_hf = QtWidgets.QLabel("HF : 0")
        self.lbl_ratio = QtWidgets.QLabel("LF/HF : 0")
        self.lbl_resp = QtWidgets.QLabel("Resp (Hz) : 0")
        self.lbl_score = QtWidgets.QLabel("Score : 0")

        right.addWidget(self.lbl_rmssd)
        right.addWidget(self.lbl_lf)
        right.addWidget(self.lbl_hf)
        right.addWidget(self.lbl_ratio)
        right.addWidget(self.lbl_resp)
        right.addWidget(self.lbl_score)

        layout.addLayout(right)

    # ------------------------------------------------------------------
    # Mise à jour du graphique de respiration guidée
    # ------------------------------------------------------------------
    def update_resp_guided_plot(self, t, y):
        self.line_resp.set_data(t, y)
        if len(t) > 1:
            self.ax_resp.set_xlim(0, t[-1])
        self.ax_resp.set_ylim(-1.2, 1.2)
        self.can_resp.draw()

    # ------------------------------------------------------------------
    # Rafraîchissement UI
    # ------------------------------------------------------------------
    def refresh_ui(self):

        # === Avancer respiration guidée ===
        self.resp_guide.step()
        insp = self.sl_insp.value()
        exp = self.sl_exp.value()
        self.resp_guide.set_durations(insp, exp)
        t, y = self.resp_guide.generate_waveform()
        self.update_resp_guided_plot(t, y)

        # === Process HRV ===
        state = self.processor.compute_state()

        # --- RR graph ---
        if len(state.rr_list) > 2:
            x = np.arange(len(state.rr_list))
            self.line_rr.set_data(x, state.rr_list)
            self.ax_rr.set_xlim(0, len(state.rr_list))
            self.ax_rr.set_ylim(min(state.rr_list) - 50,
                                max(state.rr_list) + 50)
            self.can_rr.draw()

        # --- Spectre ---
        if len(state.freq) > 2:
            self.line_spec.set_data(state.freq, state.power)
            self.ax_spec.set_xlim(0, 0.5)
            self.ax_spec.set_ylim(0, max(state.power) * 1.1)
            self.can_spec.draw()

        # --- HRV Infos ---
        self.lbl_rmssd.setText(f"RMSSD : {state.rmssd:.1f}")
        self.lbl_lf.setText(f"LF : {state.lf:.3f}")
        self.lbl_hf.setText(f"HF : {state.hf:.3f}")
        self.lbl_ratio.setText(f"LF/HF : {state.lf_hf_ratio:.3f}")
        self.lbl_resp.setText(f"Resp (Hz) : {state.resp_freq:.3f}")
        self.lbl_score.setText(f"Score : {state.score:.1f}")

        # --- Respiration estimée (orange) ---
        if state.resp_signal is not None and len(state.resp_signal) > 2:
            self.line_resp_est.set_data(state.resp_time, state.resp_signal)
            self.ax_resp.set_xlim(min(state.resp_time),
                                  max(state.resp_time))
            self.ax_resp.set_ylim(min(state.resp_signal),
                                  max(state.resp_signal))
            self.can_resp.draw()
