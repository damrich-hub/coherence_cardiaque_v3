# global_score.py
# -------------------------------------------------------
# Score global cohérence cardiaque (V10)
#
# Mélange pondéré :
#   - ratio LF/HF (40%)
#   - HF fraction (30%)
#   - Respiration (20%)
#   - RMSSD (10%)
#
# Toutes les valeurs sont déjà normalisées par Processor
# -------------------------------------------------------

class GlobalScore:
    """
    Calcule le score global final (0..100) à partir :
        - ratio_norm     (0..1)
        - hf_fraction    (0..1)
        - rmssd_norm     (0..1)
        - resp_component (0..1)
    """

    @staticmethod
    def compute(ratio_norm, hf_fraction, rmssd_norm, resp_component):
        """
        Retourne un score sur 100.
        """

        # Sécurité : clamp
        def clamp(v):
            return max(0.0, min(1.0, float(v)))

        ratio_norm     = clamp(ratio_norm)
        hf_fraction    = clamp(hf_fraction)
        rmssd_norm     = clamp(rmssd_norm)
        resp_component = clamp(resp_component)

        # Pondération V10
        score = (
            0.40 * ratio_norm +
            0.30 * hf_fraction +
            0.20 * resp_component +
            0.10 * rmssd_norm
        )

        return 100.0 * clamp(score)
