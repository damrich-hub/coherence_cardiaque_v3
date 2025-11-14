"""
signals.py
----------------
Signaux Qt utilisés dans l’application.
"""

from PySide6.QtCore import QObject, Signal


class AppSignals(QObject):
    rr_sample = Signal(float, float)
    hrv_spectral = Signal(float, float, float)
    respiration_estimated = Signal(float, float)
    score_updated = Signal(float)
