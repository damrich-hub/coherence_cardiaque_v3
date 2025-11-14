# app/graphs/__init__.py

"""
Sous-module UI : graphes principaux de l'application.

- RRGraph           : affichage des intervalles RR (ms) dans le temps
- SpectralGraph     : affichage des composantes LF / HF + ratio
- RespirationGraph  : affichage respiration guidée + respiration réelle / sinus

Chaque graphe est un QWidget contenant un canvas Matplotlib.
"""

from .rr_graph import RRGraph
from .spectral_graph import SpectralGraph
from .respiration_graph import RespirationGraph

__all__ = ["RRGraph", "SpectralGraph", "RespirationGraph"]
