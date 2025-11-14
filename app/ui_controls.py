# app/ui_controls.py
"""
ui_controls.py
--------------
Panneau de contrôle de l’application :
- Bouton connexion Polar H10
- Statuts BLE / RR / Score
- Sliders inspiration / expiration
- Affichage du score global
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSlider,
)


class ControlPanel(QWidget):
    """
    Panneau supérieur avec :
    - bouton BLE
    - statuts
    - sliders respi
    - score global
    """

    # Signaux vers MainWindow
    connect_clicked = Signal()
    insp_changed = Signal(int)
    exp_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # ------------------- Ligne BLE + statuts -------------------
        top = QHBoxLayout()
        layout.addLayout(top)

        self.btn_connect = QPushButton("Connecter Polar H10")
        self.btn_connect.clicked.connect(self.connect_clicked.emit)
        top.addWidget(self.btn_connect)

        self.lbl_ble = QLabel("BLE : 🔴 Déconnecté")
        self.lbl_rr = QLabel("RR : ⚪")
        self.lbl_score_status = QLabel("Score : ⚪")

        for lbl in (self.lbl_ble, self.lbl_rr, self.lbl_score_status):
            lbl.setStyleSheet("font-size: 13px;")
            top.addWidget(lbl)

        top.addStretch(1)

        # ------------------- Ligne sliders respi -------------------
        sliders = QHBoxLayout()
        layout.addLayout(sliders)

        self.lbl_insp = QLabel("Inspiration (s):")
        self.lbl_exp = QLabel("Expiration (s):")

        self.sl_insp = QSlider(Qt.Horizontal)
        self.sl_insp.setRange(2, 8)
        self.sl_insp.setValue(4)
        self.sl_insp.valueChanged.connect(self.insp_changed.emit)

        self.sl_exp = QSlider(Qt.Horizontal)
        self.sl_exp.setRange(2, 12)
        self.sl_exp.setValue(6)
        self.sl_exp.valueChanged.connect(self.exp_changed.emit)

        sliders.addWidget(self.lbl_insp)
        sliders.addWidget(self.sl_insp, stretch=1)
        sliders.addWidget(self.lbl_exp)
        sliders.addWidget(self.sl_exp, stretch=1)

        # ------------------- Score global -------------------
        self.lbl_score = QLabel("Score global : —")
        self.lbl_score.setAlignment(Qt.AlignCenter)
        self.lbl_score.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(self.lbl_score)

    # ==========================================================
    #   Accès sliders
    # ==========================================================
    def get_inspiration(self) -> int:
        return int(self.sl_insp.value())

    def get_expiration(self) -> int:
        return int(self.sl_exp.value())

    # ==========================================================
    #   Mise à jour des statuts
    # ==========================================================
    def set_ble_status(self, connected: bool | None, message: str | None = None):
        """
        connected :
            True  → vert
            False → rouge
            None  → jaune (en cours)
        """
        if message is None:
            if connected is True:
                message = "Connecté"
            elif connected is False:
                message = "Déconnecté"
            else:
                message = "Connexion…"

        if connected is True:
            self.lbl_ble.setText(f"BLE : 🟢 {message}")
        elif connected is False:
            self.lbl_ble.setText(f"BLE : 🔴 {message}")
        else:
            self.lbl_ble.setText(f"BLE : 🟡 {message}")

    def set_rr_status(self, ok: bool):
        self.lbl_rr.setText("RR : 🟢" if ok else "RR : 🔴")

    def set_score_status(self, ok: bool):
        self.lbl_score_status.setText("Score : 🟢" if ok else "Score : ⚪")

    def set_score_value(self, score: float):
        self.lbl_score.setText(f"Score global : {score:0.0f}")
