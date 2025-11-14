# -*- coding: utf-8 -*-
"""
test_score.py
--------------
Tests unitaires simples pour le module `score`.
Vérifie les normalisations, la synchronisation et le score global.
"""

from score.normalizers import norm_ratio, norm_hf_frac, norm_rmssd, norm_resp
from score.components import compute_sync_score
from score.global_score import compute_global_score
from score.score_colors import color_for_value


def test_normalizers():
    print("=== TEST NORMALISERS ===")
    print("LF/HF (1.0) ->", norm_ratio(1000, 1000))
    print("HF% (0.6) ->", norm_hf_frac(400, 600))
    print("RMSSD (40 ms) ->", norm_rmssd(40))
    print("Resp (6 cpm) ->", norm_resp(6))
    print("Resp (5 cpm) ->", norm_resp(5))
    print()


def test_sync_score():
    print("=== TEST SYNC% ===")
    rr = [1000, 1020, 980, 1005, 995, 1010, 1000, 990, 1015, 1005]
    sync = compute_sync_score(rr, resp_cpm=6.1, resp_quality=0.85)
    print(f"Sync% = {sync:.1f}")
    print()


def test_global_score():
    print("=== TEST GLOBAL SCORE ===")
    lf, hf, rmssd, resp_comp = 1200, 1000, 45, 0.8
    score = compute_global_score(lf, hf, rmssd, resp_comp)
    print(f"Score global : {score:.1f}")
    print()


def test_colors():
    print("=== TEST COULEURS ===")
    for name, val in [("SDNN", 25), ("SDNN", 45), ("SDNN", 80),
                      ("RMSSD", 20), ("RMSSD", 40), ("RMSSD", 70),
                      ("LFHF", 0.4), ("LFHF", 1.0), ("LFHF", 2.5),
                      ("SCORE", 30), ("SCORE", 55), ("SCORE", 85)]:
        col = color_for_value(name, val)
        print(f"{name:<6} {val:>5} → {col}")
    print()


if __name__ == "__main__":
    print("\n=== TESTS MODULE SCORE ===\n")
    test_normalizers()
    test_sync_score()
    test_global_score()
    test_colors()
    print("✅ Tests terminés.")
