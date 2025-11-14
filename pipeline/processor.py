# pipeline/processor.py
# ---------------------
# Pipeline HRV simplifié, sans respiration réelle (EDR).
#
# Utilise :
#   - hrv.time_domain.compute_time_domain(rr_ms)
#   - hrv.spectral.compute_spectral(rr_ms)
#
# Renvoie un ProcessorState contenant :
#   rmssd, lf, hf, lf_hf_ratio, resp_freq, score,
#   spec_freq, spec_power
#
# NOTE : la fonction compute_spectral peut retourner
#   soit un dict, soit un tuple ; on gère les deux cas.

from __future__ import annotations

from dataclasses import dataclass
from collections import deque
import math
from typing import Deque, Optional, Sequence

import numpy as np

from hrv.time_domain import compute_time_domain
from hrv.spectral import compute_spectral


@dataclass
class ProcessorState:
    # time-domain
    rmssd: float = 0.0

    # spectral
    lf: float = 0.0
    hf: float = 0.0
    lf_hf_ratio: float = 0.0
    resp_freq: float = 0.0  # fréquence respiratoire estimée (Hz)

    # score global (0..100)
    score: float = 0.0

    # spectre complet pour l’affichage
    spec_freq: Optional[np.ndarray] = None
    spec_power: Optional[np.ndarray] = None


class Processor:
    """
    Gère l’historique RR et calcule périodiquement un ProcessorState.

    API utilisée par MainWindow :
        - add_rr(rr_ms: float)
        - compute_state() -> ProcessorState
        - rr_history : séquence des RR ms
    """

    def __init__(
        self,
        window_sec: int = 120,
        rr_min: int = 300,
        rr_max: int = 2000,
        approx_fs: float = 4.0,
    ):
        """
        window_sec  : durée approx de la fenêtre RR (en secondes)
        rr_min/max  : bornes de filtrage des RR aberrants
        approx_fs   : fréquence d’échantillonnage supposée (Hz)
        """
        # hypothèse : ~2 battements / s → maxlen = window_sec * 2
        self.rr_history: Deque[float] = deque(maxlen=window_sec * 2)
        self._rr_min = rr_min
        self._rr_max = rr_max
        self._fs = approx_fs

        self.state = ProcessorState()

    # --------------------------------------------------
    # Données d’entrée
    # --------------------------------------------------
    def add_rr(self, rr_ms: float) -> None:
        """
        Ajoute un intervalle RR (en millisecondes), avec filtrage simple.
        """
        if rr_ms <= 0:
            return
        if rr_ms < self._rr_min or rr_ms > self._rr_max:
            # on ignore les outliers grossiers
            return

        self.rr_history.append(float(rr_ms))

    # --------------------------------------------------
    # Calcul de l’état
    # --------------------------------------------------
    def compute_state(self) -> ProcessorState:
        """
        Calcule les métriques HRV à partir de rr_history.

        Peut être appelé fréquemment par l’UI ; si les données sont
        insuffisantes, on renvoie l’état courant (principalement des zéros).
        """
        if len(self.rr_history) < 10:
            # pas assez de données pour une HRV fiable
            return self.state

        rr = np.array(self.rr_history, dtype=float)

        # -----------------------------
        # Domaine temporel
        # -----------------------------
        try:
            td = compute_time_domain(rr)
            rmssd = float(td.get("rmssd", 0.0))
        except Exception:
            rmssd = 0.0

        # -----------------------------
        # Domaine fréquentiel
        # -----------------------------
        lf = hf = peak_hf = 0.0
        freq = power = None

        try:
            spec_res = compute_spectral(rr)

            # Cas 1 : dict
            if isinstance(spec_res, dict):
                freq = np.asarray(spec_res.get("freq")) if spec_res.get("freq") is not None else None
                power = np.asarray(spec_res.get("power")) if spec_res.get("power") is not None else None
                lf = float(spec_res.get("lf", 0.0))
                hf = float(spec_res.get("hf", 0.0))
                peak_hf = float(spec_res.get("peak_hf", 0.0))

            # Cas 2 : tuple/list
            elif isinstance(spec_res, (tuple, list)) and len(spec_res) >= 2:
                freq = np.asarray(spec_res[0]) if spec_res[0] is not None else None
                power = np.asarray(spec_res[1]) if spec_res[1] is not None else None
                if len(spec_res) >= 4:
                    lf = float(spec_res[2])
                    hf = float(spec_res[3])
                if len(spec_res) >= 5:
                    peak_hf = float(spec_res[4])

        except Exception:
            # en cas d’erreur, on laisse les valeurs à 0 / None
            pass

        # Ratio LF/HF
        if hf > 1e-9:
            ratio = lf / hf
        else:
            ratio = 0.0

        # Fréquence respiratoire estimée
        resp_freq = peak_hf if peak_hf > 0 else 0.0

        # -----------------------------
        # Score global (0..100)
        # -----------------------------
        score = self._compute_score(rmssd, lf, hf, ratio, resp_freq)

        # -----------------------------
        # Mise à jour de l’état
        # -----------------------------
        self.state = ProcessorState(
            rmssd=rmssd,
            lf=lf,
            hf=hf,
            lf_hf_ratio=ratio,
            resp_freq=resp_freq,
            score=score,
            spec_freq=freq,
            spec_power=power,
        )

        return self.state

    # --------------------------------------------------
    # Score global (très simple mais stable)
    # --------------------------------------------------
    def _compute_score(
        self,
        rmssd: float,
        lf: float,
        hf: float,
        ratio: float,
        resp_freq: float,
    ) -> float:
        """
        Combinaison très simple de trois composantes :
        - ratio LF/HF proche de 1
        - RMSSD "suffisant"
        - respiration autour de 0.1 Hz (~6 cpm)

        Renvoie un score entre 0 et 100.
        """

        # RMSSD : normaliser avec plafond ~80 ms
        rmssd_norm = max(0.0, min(rmssd / 80.0, 1.0))

        # Ratio LF/HF : optimum autour de 1 (0.5–2)
        if hf <= 0 or lf <= 0:
            ratio_norm = 0.0
        else:
            r = max(ratio, 1e-8)
            # plus r est proche de 1, plus le score est bon
            ratio_norm = 1.0 - min(abs(math.log10(r)), 1.0)
            ratio_norm = max(0.0, min(ratio_norm, 1.0))

        # Respiration : maximum à 0.1 Hz (6 respirations/min)
        if resp_freq <= 0:
            resp_norm = 0.0
        else:
            # distance relative à 0.1 Hz, tolérance ±0.05 Hz
            diff = abs(resp_freq - 0.1)
            resp_norm = 1.0 - min(diff / 0.05, 1.0)
            resp_norm = max(0.0, resp_norm)

        # pondération simple
        score_0_1 = 0.4 * ratio_norm + 0.3 * rmssd_norm + 0.3 * resp_norm
        return float(max(0.0, min(score_0_1, 1.0)) * 100.0)
