# ble/ble_worker.py
# -----------------
# Version simple : génère des intervalles RR simulés.
# Objectif : avoir une source de données stable pour tester
# l’UI et le pipeline sans s’occuper du BLE réel.
#
# Plus tard, on pourra réintroduire la logique Polar H10
# (Bleak, UUID, etc.) dans cette même classe.

from PySide6 import QtCore
import random


class BLEWorker(QtCore.QObject):
    """
    Générateur simple de RR simulés.

    new_rr_signal : émet un RR en millisecondes (int)
    toutes les secondes environ.
    """

    new_rr_signal = QtCore.Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(1000)  # 1 RR / seconde
        self._timer.timeout.connect(self._emit_fake_rr)

        # On démarre tout de suite la simulation
        self._timer.start()

    # --------------------------------------------------
    # API minimale (start/stop) si tu veux contrôler
    # depuis main.py ou un bouton plus tard.
    # --------------------------------------------------
    def start(self):
        if not self._timer.isActive():
            self._timer.start()

    def stop(self):
        if self._timer.isActive():
            self._timer.stop()

    # --------------------------------------------------
    # Génération RR factice
    # --------------------------------------------------
    def _emit_fake_rr(self):
        """
        Génère un RR autour de 800 ms avec un peu de bruit.
        """
        base_rr = 800  # ms
        jitter = random.randint(-60, 60)
        rr = base_rr + jitter
        self.new_rr_signal.emit(int(rr))
