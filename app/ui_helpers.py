# app/ui_helpers.py
# -----------------
# Contient des helpers UI réutilisables :
# - make_led : petit widget rond type LED (rouge/vert/jaune)
# - color manipulation

from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt


class LedWidget(QLabel):
    """
    Petite LED ronde : on/off + couleur.
    Utilisée pour BLE, RR, Score.
    """

    def __init__(self, diameter=14, color_on="#00cc00", color_off="#cc0000"):
        super().__init__()

        self.diameter = diameter
        self.color_on = QColor(color_on)
        self.color_off = QColor(color_off)
        self._is_on = False

        self.setFixedSize(diameter + 2, diameter + 2)
        self.setAlignment(Qt.AlignCenter)
        self._update_style()

    # ------------------------------------------------
    def _update_style(self):
        color = self.color_on if self._is_on else self.color_off
        self.setStyleSheet(
            f"""
            background-color: {color.name()};
            border-radius: {self.diameter // 2}px;
            border: 1px solid #444;
            """
        )

    # ------------------------------------------------
    def set_on(self, value: bool):
        """Allume/éteint la LED."""
        self._is_on = bool(value)
        self._update_style()


# ----------------------------------------------------------------------
# Helper : fabrique rapidement une LED
# ----------------------------------------------------------------------
def make_led(color_on="#00dd00", color_off="#dd0000"):
    """
    Fabrique une LED prête à l’emploi.
    """
    return LedWidget(diameter=14, color_on=color_on, color_off=color_off)
