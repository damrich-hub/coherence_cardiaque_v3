# polar_constants.py
# -------------------
# Constantes BLE pour Polar H10 (toutes versions)
#
# Pour un Polar H10 V1 :
#   - Seul le service standard "Heart Rate Measurement" est disponible
#   - UUID = 00002a37-0000-1000-8000-00805f9b34fb
#
# Pas de service ECG, pas de service propriétaire Polar BLE SDK

POLAR_H10_NAME = "Polar H10"

# Heart Rate Measurement (RR intervals inside)
POLAR_H10_UUID = "00002a37-0000-1000-8000-00805f9b34fb"
