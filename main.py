from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl
from PyQt6 import uic
import sys
import bend
import stretch
import about


class mainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/mainWindow.ui", self)  # load the ui file
        self.actionAbout.triggered.connect(self.onclick_about)
        self.actionGetStarted.triggered.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile("./doc/Get started.mp4")))
        self.actionDocumentation.triggered.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile("./doc/thesis.pdf")))

        self.pushButton_stretch.clicked.connect(self.onclick_stretch)
        self.pushButton_bend.clicked.connect(self.onclick_bend)

    def onclick_bend(self):
        bend_window = bend.BendWindow()
        bend_window.show()

    def onclick_stretch(self):
        stretch_window = stretch.StretchWindow()
        stretch_window.show()

    def onclick_about(self):
        self.about_window = about.AboutWindow()
        self.about_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = mainWindow()
    window.show()
    sys.exit(app.exec())
