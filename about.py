from PyQt6.QtWidgets import QWidget, QApplication
import sys
from PyQt6 import uic
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl


class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/about.ui", self)  # load the ui file
        self.pushButton_github.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl('https://github.com/wangyang3c/Masterarbeit/tree/main/PC/formal')))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AboutWindow()
    window.show()
    sys.exit(app.exec())
