"""
buffers.py
-----------
Implémente des structures simples pour stocker les valeurs RR reçues depuis
le capteur ble.

Ces buffers sont utilisés par :
- le module ble worker
- les modules hrv / edr
"""

from collections import deque
from typing import Deque, List


class RRBuffer:
    """
    Buffer circulaire pour stocker les intervalles RR en millisecondes.
    - maxlen défini la fenêtre temporelle (ex: 120s)
    - append() pour ajouter un RR
    - get() pour récupérer la liste actuelle
    """

    def __init__(self, maxlen: int = 3000):
        self._buf: Deque[float] = deque(maxlen=maxlen)

    def append(self, value: float) -> None:
        self._buf.append(value)

    def clear(self) -> None:
        self._buf.clear()

    def get(self) -> List[float]:
        return list(self._buf)

    def __len__(self) -> int:
        return len(self._buf)
