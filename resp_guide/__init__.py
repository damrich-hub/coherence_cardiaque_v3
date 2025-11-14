"""
Module resp_guide
-----------------
Génère et met à jour la respiration guidée :
- Calcul de la phase (inspiration / expiration)
- Position du point courant
- Courbe sinus ou modèle personnalisé
- Gestion stable du temps, indépendante de l'interface

Ce module fournit une API simple :
    guide = RespGuide(cpm=6)
    value = guide.value(t)
    phase = guide.phase(t)
    curve  = guide.generate_curve(window=20)

L’objectif est d’isoler complètement la logique du guide respiratoire pour
rendre la fenêtre principale plus légère et mieux structurée.
"""
