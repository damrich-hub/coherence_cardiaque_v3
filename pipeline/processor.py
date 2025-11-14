# pipeline/processor.py

import numpy as np
from dataclasses import dataclass

from hrv.time_domain import compute_time_domain
from hrv.spectral import compute_spectral


# ----------------------------------------------------------------------
# ProcessorState : état complet envoyé à l'UI
# ----------------------------------------------------------------------
@dataclass
class ProcessorState:
    rr_list: list
    rmssd: float
    lf: float
    hf: float
    lf_hf_ratio: float
    resp_freq: float
    freq: np.ndarray
    power: np.ndarray
    score: float

    # Respiration estimée (RSA / EDR)
    resp_signal: np.ndarray = None
    resp_time: np.ndarray = None


# ----------------------------------------------------------------------
# Processor : cœur du traitement HRV
# ----------------------------------------------------------------------
class Processor:
    def __init__(self, max_window=300):  # ~ 300 RR ≈ 4 minutes
        self.rr_list = []
        self.max_window = max_window

    # --------------------------------------------------------------
    def push_rr(self, rr):
        """Ajoute un RR et maintient une fenêtre glissante."""
        self.rr_list.append(int(rr))

        # fenêtre glissante (max 4 minutes)
        if len(self.rr_list) > self.max_window:
            self.rr_list = self.rr_list[-self.max_window:]

    # --------------------------------------------------------------
    def compute_state(self) -> ProcessorState:
        """Calcule tous les indicateurs HRV + spectre + score + respiration estimée."""
        rr = self.rr_list

        # Cas de base si pas assez de données
        if len(rr) < 4:
            return ProcessorState(
                rr_list=rr,
                rmssd=0.0,
                lf=0.0,
                hf=0.0,
                lf_hf_ratio=0.0,
                resp_freq=0.0,
                freq=np.array([]),
                power=np.array([]),
                score=0.0,
                resp_signal=np.array([]),
                resp_time=np.array([]),
            )

        # ====== 1) TIME DOMAIN ======
        td = compute_time_domain(rr)
        rmssd = td.get("rmssd", 0.0)

        # ====== 2) SPECTRAL ======
        spec = compute_spectral(rr)

        if spec["freq"] is not None:
            freq = spec["freq"]
            power = spec["power"]
            lf = spec["lf"]
            hf = spec["hf"]
            ratio = lf / hf if hf > 1e-9 else 0.0
            resp_freq = spec.get("peak_hf", 0.0)
        else:
            freq = np.array([])
            power = np.array([])
            lf = hf = ratio = resp_freq = 0.0

        # ====== 3) SCORE SIMPLE ======
        score = float(min(100.0, rmssd / 3.0 * 100.0))

        # ====== 4) RESPIRATION ESTIMÉE (RSA / EDR) ======

        # Variation des RR : c’est la base du RSA
        rr_array = np.array(rr)
        rr_diff = rr_array - np.mean(rr_array)

        # Normalisation pour tracer
        if len(rr_diff) > 4:
            resp_signal = rr_diff / (np.max(np.abs(rr_diff)) + 1e-9)
        else:
            resp_signal = np.array([])

        resp_time = np.arange(len(resp_signal))

        # Retour complet
        return ProcessorState(
            rr_list=rr,
            rmssd=rmssd,
            lf=lf,
            hf=hf,
            lf_hf_ratio=ratio,
            resp_freq=resp_freq,
            freq=freq,
            power=power,
            score=score,
            resp_signal=resp_signal,
            resp_time=resp_time,
        )
