# -*- coding: utf-8 -*-
"""
ble/exceptions.py
-----------------
Définitions des exceptions spécifiques à la couche BLE (Bluetooth Low Energy).

Objectif :
    - Centraliser les erreurs liées au scan, à la connexion et à la lecture des données.
    - Permettre une gestion uniforme dans le BLEWorker et l'interface utilisateur.

Chaque exception fournit :
    - Un message court (user-friendly)
    - Un niveau de gravité (info / warning / error)
"""

class BLEError(Exception):
    """Erreur générique BLE."""
    level = "error"

    def __init__(self, message="Erreur BLE"):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class PolarNotFoundError(BLEError):
    """Aucun Polar H10 détecté."""
    level = "warning"

    def __init__(self, message="❌ Aucun Polar H10 détecté. Vérifiez le Bluetooth."):
        super().__init__(message)


class BLEConnectionError(BLEError):
    """Erreur de connexion au périphérique BLE."""
    level = "error"

    def __init__(self, message="❌ Connexion BLE impossible."):
        super().__init__(message)


class BLENotificationError(BLEError):
    """Impossible d’activer les notifications RR (2A37)."""
    level = "error"

    def __init__(self, message="⚠️ Impossible d’activer les notifications RR."):
        super().__init__(message)


class BLEDataError(BLEError):
    """Erreur de décodage ou d’analyse des données BLE."""
    level = "warning"

    def __init__(self, message="⚠️ Données BLE invalides ou incomplètes."):
        super().__init__(message)


class BLEScanError(BLEError):
    """Erreur survenue lors du scan BLE."""
    level = "error"

    def __init__(self, message="⚠️ Erreur lors du scan BLE."):
        super().__init__(message)
