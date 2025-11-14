# main.py

from app.main_window import MainWindow
from PySide6 import QtWidgets


def main():
    app = QtWidgets.QApplication([])
    w = MainWindow()   # plus d'arguments !
    w.show()
    app.exec()


if __name__ == "__main__":
    main()
