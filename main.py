from PySide6 import QtWidgets
import sys

from app.main_window import MainWindow
from ble.ble_worker import BLEWorker
from pipeline import Processor
from resp_guide.guide import RespGuideGenerator


def main():
    app = QtWidgets.QApplication(sys.argv)

    ble_worker = BLEWorker()
    processor = Processor()
    resp_guide = RespGuideGenerator()

    w = MainWindow(ble_worker, processor, resp_guide)
    w.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
