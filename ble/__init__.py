"""
Module BLE – initialisation

Expose uniquement les classes et constantes nécessaires pour le reste du programme.
"""

from .ble_worker import BLEWorker
from .polar_constants import POLAR_H10_UUID, POLAR_H10_NAME

__all__ = [
    "BLEWorker",
    "POLAR_H10_UUID",
    "POLAR_H10_NAME",
]
