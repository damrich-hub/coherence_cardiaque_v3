import numpy as np
from typing import Iterable, Dict

def compute_time_domain(rr_ms: Iterable[float]) -> Dict[str, float]:
    """
    Renvoie un dictionnaire {"sdnn": ..., "rmssd": ...}
    conforme à ce qu'attend Processor.
    """
    rr = np.asarray(list(rr_ms), dtype=float)

    if rr.size < 2:
        return {"sdnn": 0.0, "rmssd": 0.0}

    # SDNN (écart-type)
    sdnn = float(np.std(rr, ddof=1))

    # RMSSD
    diff = np.diff(rr)
    if diff.size == 0:
        rmssd = 0.0
    else:
        rmssd = float(np.sqrt(np.mean(diff * diff)))

    return {"sdnn": sdnn, "rmssd": rmssd}
