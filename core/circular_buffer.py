"""
circular_buffer.py
------------------
Buffers circulaires génériques, thread-safe, pour stocker des séries
temps réel (ex. RR, LF/HF, score…).
"""

from collections import deque
from threading import Lock
from typing import Deque, Generic, Iterable, Iterator, List, Optional, Tuple, TypeVar

T = TypeVar("T")


class CircularBuffer(Generic[T]):
    """Buffer circulaire thread-safe d'objets de type T."""

    def __init__(self, maxlen: int):
        self._buf: Deque[T] = deque(maxlen=maxlen)
        self._lock = Lock()

    def append(self, item: T) -> None:
        with self._lock:
            self._buf.append(item)

    def extend(self, items: Iterable[T]) -> None:
        with self._lock:
            self._buf.extend(items)

    def clear(self) -> None:
        with self._lock:
            self._buf.clear()

    def snapshot(self) -> List[T]:
        """Retourne une copie *instantanée* (thread-safe)."""
        with self._lock:
            return list(self._buf)

    def __len__(self) -> int:
        with self._lock:
            return len(self._buf)

    def __iter__(self) -> Iterator[T]:
        # itère sur un snapshot pour éviter de garder le lock
        return iter(self.snapshot())


class TimeSeriesBuffer(CircularBuffer[Tuple[float, float]]):
    """
    Buffer (ts, value) pour séries temporelles.
    ts = timestamp (epoch seconds), value = flottant.
    """

    def append_point(self, ts: float, value: float) -> None:
        super().append((ts, float(value)))

    def window_since(self, t_min: float) -> List[Tuple[float, float]]:
        """Sous-série avec ts >= t_min."""
        data = self.snapshot()
        return [(t, v) for (t, v) in data if t >= t_min]

    def last(self) -> Optional[Tuple[float, float]]:
        data = self.snapshot()
        return data[-1] if data else None
