# -*- coding: utf-8 -*-
"""
test_ble.py
------------
Script de test autonome du module BLEWorker.
Permet de vérifier la détection, la connexion et la réception des RR
sans passer par l’interface graphique principale.

À lancer depuis PyCharm ou la console :
    python test_ble.py
"""

import sys
from PySide6 import QtWidgets
from ble.ble_worker import BLEWorker


def main():
    app = QtWidgets.QApplication(sys.argv)
    ble = BLEWorker()

    # Connexions des signaux Qt
    ble.status.connect(lambda msg: print(f"[STATUS] {msg}"))
    ble.connected.connect(lambda ok: print(f"[CONNECTED] {ok}"))
    ble.rr_sample.connect(lambda ts, rr: print(f"[RR] {ts:.3f} → {rr:.1f} ms"))

    print("🔧 Test BLE : démarrage du thread...")
    ble.start()

    app.exec()


if __name__ == "__main__":
    main()
