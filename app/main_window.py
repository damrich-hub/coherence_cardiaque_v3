# -*- coding: utf-8 -*-
import math
from PySide6 import QtCore, QtWidgets

import matplotlib
matplotlib.use("qtagg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)


class MainWindow(QtWidgets.QMainWindow):
    """
    Version simplifiée et cohérente avec ton architecture actuelle.
    - pas de respiration réelle EDR
    - respiration guidée OK
    - Processor OK
    - BLE OK
    """

    def __init__(self, ble_worker, processor, resp_guide):
        super().__init__()

        self.setWindowTitle("Cohérence Cardiaque – V3 Stable")
        self.resize(1200, 700)

        self.ble = ble_worker
        self.processor = processor
        self.resp_guide = resp_guide

        self._build_ui()
        self._connect_signals()

        # timer UI
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.refresh_ui)
        self.timer.start(80)

    # ------------------------------------------------------------
    # UI
    # ------------------------------------------------------------
    def _build_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QHBoxLayout(central)

        # ------------------------------
        # Left: RR + Spectre + Guide
        # ------------------------------
        left = QtWidgets.QVBoxLayout()
        layout.addLayout(left, stretch=2)

        # RR graph
        self.can_rr = MplCanvas(width=6, height=2.5)
        self.ax_rr = self.can_rr.fig.add_subplot(111)
        self.ax_rr.set_title("RR (ms)")
        self.ax_rr.grid(True, alpha=0.3)
        (self.line_rr,) = self.ax_rr.plot([], [], lw=1.4)
        self.ax_rr.set_ylim(600, 1200)
        self.ax_rr.set_xlim(0, 60)
        left.addWidget(self.can_rr)

        # Spectre HRV
        self.can_spec = MplCanvas(width=6, height=2.5)
        self.ax_spec = self.can_spec.fig.add_subplot(111)
        self.ax_spec.set_title("Spectre HRV")
        self.ax_spec.grid(True, alpha=0.3)
        (self.line_spec,) = self.ax_spec.plot([], [], lw=1.4)
        self.ax_spec.set_xlim(0, 0.5)
        self.ax_spec.set_ylim(0, 1)
        left.addWidget(self.can_spec)

        # Guide respiration
        self.can_guide = MplCanvas(width=6, height=2.2)
        self.ax_guide = self.can_guide.fig.add_subplot(111)
        self.ax_guide.set_title("Respiration guidée")
        self.ax_guide.grid(True, alpha=0.3)
        (self.line_guide,) = self.ax_guide.plot([], [], lw=1.4, color="green")
        self.ax_guide.set_xlim(0, 10)
        self.ax_guide.set_ylim(-1.2, 1.2)
        left.addWidget(self.can_guide)

        # ------------------------------
        # Right : Sliders + Stats
        # ------------------------------
        right = QtWidgets.QVBoxLayout()
        layout.addLayout(right, stretch=1)

        # sliders respiration
        box_sliders = QtWidgets.QGroupBox("Respiration guidée")
        l = QtWidgets.QVBoxLayout(box_sliders)

        self.slide_insp = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slide_insp.setRange(2, 10)
        self.slide_insp.setValue(4)

        self.slide_exp = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slide_exp.setRange(2, 10)
        self.slide_exp.setValue(6)

        l.addWidget(QtWidgets.QLabel("Inspiration (s)"))
        l.addWidget(self.slide_insp)
        l.addWidget(QtWidgets.QLabel("Expiration (s)"))
        l.addWidget(self.slide_exp)

        right.addWidget(box_sliders)

        # stats affichées
        box_stats = QtWidgets.QGroupBox("Indicateurs HRV")
        ls = QtWidgets.QFormLayout(box_stats)

        self.lbl_rmssd = QtWidgets.QLabel("0")
        self.lbl_lf = QtWidgets.QLabel("0")
        self.lbl_hf = QtWidgets.QLabel("0")
        self.lbl_ratio = QtWidgets.QLabel("0")
        self.lbl_breath = QtWidgets.QLabel("0")
        self.lbl_score = QtWidgets.QLabel("0")

        ls.addRow("RMSSD :", self.lbl_rmssd)
        ls.addRow("LF :", self.lbl_lf)
        ls.addRow("HF :", self.lbl_hf)
        ls.addRow("LF/HF :", self.lbl_ratio)
        ls.addRow("Resp (Hz) :", self.lbl_breath)
        ls.addRow("Score :", self.lbl_score)

        right.addWidget(box_stats)

        right.addStretch()

    # ------------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------------
    def _connect_signals(self):
        self.ble.new_rr_signal.connect(self._on_new_rr)

    def _on_new_rr(self, rr_value):
        """ Nouveau RR venant du BLE """
        self.processor.add_rr(rr_value)

    # ------------------------------------------------------------
    # REFRESH UI
    # ------------------------------------------------------------
    def refresh_ui(self):
        """
        Rafraîchit uniquement :
        - RR
        - spectre
        - respiration guidée
        - stats HRV (ProcessorState)
        """

        # -----------------------------
        # respiration guidée
        # -----------------------------
        insp = self.slide_insp.value()
        exp = self.slide_exp.value()

        self.resp_guide.set_times(insp, exp)
        t, y = self.resp_guide.generate_wave()

        self.line_guide.set_data(t, y)
        self.ax_guide.set_xlim(0, max(t) if len(t) > 0 else 10)
        self.can_guide.draw()

        # -----------------------------
        # calculs HRV
        # -----------------------------
        state = self.processor.compute_state()
        if state is None:
            return

        # -----------------------------
        # update RR graph
        # -----------------------------
        rr = self.processor.rr_history
        if len(rr) > 2:
            self.line_rr.set_data(range(len(rr)), rr)
            self.ax_rr.set_xlim(0, len(rr))
            self.can_rr.draw()

        # -----------------------------
        # update HRV spectrum
        # -----------------------------
        if state.spec_freq is not None and state.spec_power is not None:
            self.line_spec.set_data(state.spec_freq, state.spec_power)
            self.ax_spec.set_xlim(0, 0.5)
            if len(state.spec_power) > 0:
                self.ax_spec.set_ylim(0, max(state.spec_power) * 1.2)
            self.can_spec.draw()

        # -----------------------------
        # update labels
        # -----------------------------
        self.lbl_rmssd.setText(f"{state.rmssd:.1f}")
        self.lbl_lf.setText(f"{state.lf:.3f}")
        self.lbl_hf.setText(f"{state.hf:.3f}")
        self.lbl_ratio.setText(f"{state.lf_hf_ratio:.3f}")
        self.lbl_breath.setText(f"{state.resp_freq:.3f}")
        self.lbl_score.setText(f"{state.score:.1f}")
