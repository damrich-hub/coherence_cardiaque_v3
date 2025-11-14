"""
smoothing.py
------------
Outils de lissage en temps réel :
- EMA simple
- Low-pass "alpha" sur séries
- Anti-saut relatif
- RateLimiter pour limiter les variations par seconde
"""

from dataclasses import dataclass
from .math_utils import clamp


@dataclass
class EMA:
    """
    Moyenne exponentielle : y = (1-a)*y + a*x
    - init avec None pour suivre la première valeur sans délai
    """
    alpha: float
    y: float | None = None

    def push(self, x: float) -> float:
        if self.y is None:
            self.y = float(x)
        else:
            self.y = (1 - self.alpha) * self.y + self.alpha * float(x)
        return self.y


@dataclass
class AntiJump:
    """
    Limite les sauts relatifs > max_rel (ex: 0.25 = 25%).
    Si un saut est trop grand, on coupe au seuil.
    """
    max_rel: float = 0.25

    def apply(self, x: float, ref: float | None) -> float:
        if ref is None or ref == 0:
            return x
        rel = abs(x - ref) / abs(ref)
        if rel <= self.max_rel:
            return x
        return ref + (self.max_rel * ref) * (1 if x > ref else -1)


@dataclass
class RateLimiter:
    """
    Limite le taux de variation : |dx/dt| <= max_rate (unités par seconde).
    Passer le temps courant (t) à chaque appel.
    """
    max_rate: float
    last_t: float | None = None
    last_x: float | None = None

    def step(self, x: float, t: float) -> float:
        if self.last_t is None or self.last_x is None:
            self.last_t, self.last_x = t, float(x)
            return self.last_x
        dt = max(1e-6, t - self.last_t)
        dx = clamp(x - self.last_x, -self.max_rate * dt, self.max_rate * dt)
        self.last_x += dx
        self.last_t = t
        return self.last_x
