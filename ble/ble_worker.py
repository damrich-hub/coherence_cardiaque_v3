# ble/ble_worker.py

import random
from PySide6 import QtCore


class BLEWorker(QtCore.QObject):
    """
    Simulation BLE :
      - génère des RR aléatoires autour de 800 ms
      - émet un signal de statut pour l'UI
    """

    new_rr_signal = QtCore.Signal(int)
    status_signal = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.generate_rr)

    def start(self):
        """Démarre la simulation."""
        self.status_signal.emit("Simulation active")
        self.timer.start(600)   # ~100 bpm simulés

    def stop(self):
        """Arrête la simulation."""
        self.status_signal.emit("Arrêt")
        self.timer.stop()

    def generate_rr(self):
        """
        Génère un RR réaliste :
        800 ms ± 60 ms, jamais en dessous de 500 ms.
        """
        base_rr = 800
        noise = random.randint(-60, 60)
        rr = max(500, base_rr + noise)
        self.new_rr_signal.emit(rr)
