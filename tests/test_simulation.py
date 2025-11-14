# -*- coding: utf-8 -*-
"""
test_simulation.py
------------------
Simulateur Premium avec sliders crantés et guide respiratoire fluide.
"""

import sys
import time
import math
import numpy as np
from PySide6 import QtCore, QtWidgets
from app.main_window import MainWindow


# ---------------------------------------------------------------------
# Simulation BLE
# ---------------------------------------------------------------------
class FakeBLE(QtCore.QThread):
    rr_sample = QtCore.Signal(float, float)
    status = QtCore.Signal(str)
    connected = QtCore.Signal(bool)

    def __init__(self, parent=None, base_hr_bpm=75.0, inh=4.0, exh=6.0):
        super().__init__(parent)
        self.running = False
        self.base_hr_bpm = base_hr_bpm
        self.inh = inh
        self.exh = exh
        self.t0 = time.time()

    @property
    def resp_cpm(self) -> float:
        T = max(0.1, self.inh + self.exh)
        return 60.0 / T

    def run(self):
        self.running = True
        self.status.emit("Connexion simulée (mode test)")
        self.connected.emit(True)
        t = 0.0
        while self.running:
            base_rr = 60000.0 / self.base_hr_bpm
            freq_resp = self.resp_cpm / 60.0
            mod = 50.0 * math.sin(2 * math.pi * freq_resp * t)
            rr = base_rr + mod + np.random.randn() * 5.0
            ts = time.time()
            self.rr_sample.emit(ts, rr)
            t += rr / 1000.0
            time.sleep(rr / 1000.0)
        self.connected.emit(False)
        self.status.emit("Simulation arrêtée.")

    def stop(self):
        self.running = False


# ---------------------------------------------------------------------
# Fenêtre principale simulée
# ---------------------------------------------------------------------
class TestWindow(MainWindow):
    """Fenêtre principale avec BLE simulé + sliders inspi/expi + guide fluide"""
    def __init__(self):
        super().__init__()

        # Arrêt du vrai BLEWorker
        try:
            self.ble.stop()
            self.ble.wait(1000)
        except Exception:
            pass

        # Simulateur BLE
        self.ble = FakeBLE(self, base_hr_bpm=75.0, inh=4.0, exh=6.0)
        self.ble.status.connect(self._on_ble_status)
        self.ble.connected.connect(self._on_ble_connected)
        self.ble.rr_sample.connect(self._on_rr_sample)

        # LED verte
        self.lbl_ble_text.setText("BLE : connecté ✅")
        self.led_ble.setStyleSheet("""
            QLabel {
                background-color: #44cc44;
                border-radius: 9px;
                border: 1px solid #333;
            }
        """)

        self.ble.start()

        self.inh = self.ble.inh
        self.exh = self.ble.exh
        self.phase_t = 0.0  # temps interne du guide

        self.setWindowTitle("Simulation Cohérence Cardiaque – Mode Test")

        self._add_resp_control()

        # Timer pour le guide respiratoire fluide
        self._guide_timer = QtCore.QTimer(self)
        self._guide_timer.setInterval(33)  # ≈ 30 FPS
        self._guide_timer.timeout.connect(self._update_breath_guide)
        self._guide_timer.start()

    # -----------------------------------------------------------------
    def _add_resp_control(self):
        """Ajoute les sliders inspi/expi crantés."""
        ctrl_frame = QtWidgets.QFrame()
        ctrl_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 8px;
            }
        """)
        layout = QtWidgets.QGridLayout(ctrl_frame)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(6)

        lbl_inh = QtWidgets.QLabel("Inspiration (s) :")
        lbl_inh.setStyleSheet("QLabel { font-weight: 600; }")
        self.slider_inh = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_inh.setRange(20, 60)
        self.slider_inh.setTickInterval(5)
        self.slider_inh.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.slider_inh.setValue(int(self.inh * 10))
        self.slider_inh.valueChanged.connect(self._on_resp_change)
        self.lbl_inh_val = QtWidgets.QLabel(f"{self.inh:.1f} s")

        lbl_exh = QtWidgets.QLabel("Expiration (s) :")
        lbl_exh.setStyleSheet("QLabel { font-weight: 600; }")
        self.slider_exh = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_exh.setRange(30, 80)
        self.slider_exh.setTickInterval(5)
        self.slider_exh.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.slider_exh.setValue(int(self.exh * 10))
        self.slider_exh.valueChanged.connect(self._on_resp_change)
        self.lbl_exh_val = QtWidgets.QLabel(f"{self.exh:.1f} s")

        self.lbl_cpm = QtWidgets.QLabel(f"→ {self.ble.resp_cpm:.1f} cpm")
        self.lbl_cpm.setStyleSheet("QLabel { font-weight: 600; color: #333; }")
        self.lbl_cpm.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        layout.addWidget(lbl_inh, 0, 0)
        layout.addWidget(self.slider_inh, 0, 1)
        layout.addWidget(self.lbl_inh_val, 0, 2)
        layout.addWidget(lbl_exh, 1, 0)
        layout.addWidget(self.slider_exh, 1, 1)
        layout.addWidget(self.lbl_exh_val, 1, 2)
        layout.addWidget(self.lbl_cpm, 2, 0, 1, 3)

        self.centralWidget().layout().itemAt(0).layout().addWidget(ctrl_frame)

    # -----------------------------------------------------------------
    def _on_resp_change(self):
        """Mise à jour du rythme respiratoire."""
        self.inh = round(self.slider_inh.value() / 10.0, 1)
        self.exh = round(self.slider_exh.value() / 10.0, 1)
        self.ble.inh = self.inh
        self.ble.exh = self.exh
        cpm = self.ble.resp_cpm
        self.lbl_inh_val.setText(f"{self.inh:.1f} s")
        self.lbl_exh_val.setText(f"{self.exh:.1f} s")
        self.lbl_cpm.setText(f"→ {cpm:.1f} cpm")

    # -----------------------------------------------------------------
    def _update_breath_guide(self):
        """Affichage fluide du guide respiratoire."""
        dt = 0.033  # pas temps (33 ms)
        self.phase_t += dt

        T = self.inh + self.exh
        if T <= 0:
            return

        tt = np.linspace(-20.0, 0.0, 400)
        t_abs = self.phase_t + tt
        ph = np.mod(t_abs, T)
        vals = np.zeros_like(tt)

        insp = ph < self.inh
        prog = ph / self.inh
        e = (ph - self.inh) / self.exh
        vals[insp] = 0.5 + 0.5 * np.sin(np.pi * (prog[insp] - 0.5))
        vals[~insp] = 0.5 + 0.5 * np.sin(np.pi * (1.0 - e[~insp] - 0.5))
        vals = np.clip(vals, 0, 1)

        self.line_guide.set_data(tt, vals)
        self.can_br.draw_idle()


# ---------------------------------------------------------------------
def main():
    app = QtWidgets.QApplication(sys.argv)
    w = TestWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
