"""
debug.py
--------
Petit outillage de logging et de profilage.
"""

import logging
import time
from contextlib import contextmanager
from functools import wraps


def setup_logger(name: str = "coherence", level: int = logging.INFO) -> logging.Logger:
    """Configure un logger simple (console)."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        h = logging.StreamHandler()
        fmt = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
        h.setFormatter(fmt)
        logger.addHandler(h)
    return logger


@contextmanager
def timeblock(label: str, logger: logging.Logger | None = None):
    """Mesure le temps d'un bloc avec `with timeblock('X'):`"""
    t0 = time.perf_counter()
    try:
        yield
    finally:
        dt = (time.perf_counter() - t0) * 1000.0
        msg = f"{label} took {dt:.1f} ms"
        (logger or setup_logger()).info(msg)


def log_exceptions(logger: logging.Logger | None = None):
    """Décorateur : logge les exceptions et les relance."""
    lg = logger or setup_logger()
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            try:
                return fn(*a, **kw)
            except Exception as e:
                lg.exception(f"Exception in {fn.__name__}: {e}")
                raise
        return wrapper
    return deco
