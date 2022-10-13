import sys
import os
import qdarktheme

from PyQt5 import QtWidgets, QtGui, QtCore

from binbuilder import __version__ as package_version


def textDisplayWindow(title, message):
    msg = QtWidgets.QMessageBox()
    msg.setInformativeText(message)
    msg.setWindowTitle(title)
    #self.setWindowIcon(QtGui.QIcon(ICON_PATH))
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg.exec_()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, primary_screen):
        super(MainWindow, self).__init__()

        self.default_palette = QtWidgets.QApplication.instance().palette()
        self.primary_screen = primary_screen
        self.initUi()

    def initUi(self):
        #self.iconPath = ICON_PATH
        #self.setWindowIcon(QtGui.QIcon(self.iconPath))

        #self.widget = MainWidget(self.primary_screen, self)
        #self.setCentralWidget(self.widget)

        #self.quitActdion = QtWidgets.QAction("Quit program", self)
        #self.quitAction.setShortcut("Ctrl+q")
        #self.quitAction.setStatusTip("Close the program")
        #self.quitAction.triggered.connect(self.widget.quit)

        self.darkThemeAction = QtWidgets.QAction("Dark theme", self)
        self.darkThemeAction.setShortcut("Ctrl+v")
        self.darkThemeAction.setStatusTip("Enable/disable dark theme")
        self.darkThemeAction.triggered.connect(self.toggleDarkTheme)
        self.darkThemeAction.setCheckable(True)
        self.darkThemeAction.setChecked(True)

        # Build menu bar
        menu = self.menuBar()
        #fileMenu = menu.addMenu("File")
        #fileMenu.addAction(self.quitAction)

        viewMenu = menu.addMenu("View")
        viewMenu.addAction(self.darkThemeAction)

    def enableDarkTheme(self, enabled):
        app = QtWidgets.QApplication.instance()

        if enabled:
            app.setPalette(qdarktheme.load_palette())
        else:
            app.setPalette(self.default_palette)

        app.setStyle('Fusion')
        app.setStyleSheet("")

    def toggleDarkTheme(self):
        self.enableDarkTheme(self.darkThemeAction.isChecked())

    def closeEvent(self, event):
        if self.widget.warningBeforeQuit():
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    app.setStyle('Fusion')
    font = QtWidgets.qApp.font()
    font.setPointSize(12)
    font.setFamily('monospace')
    app.setFont(font)

    win = MainWindow(app.primaryScreen())
    win.setWindowTitle("binbuilder %s" % package_version)
    win.enableDarkTheme(True)
    win.show()

    sys.exit(app.exec_())