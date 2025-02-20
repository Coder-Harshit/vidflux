import sys
from PySide6 import QtCore, QtWidgets, QtGui
from screens.home import HomeWidget

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    home = HomeWidget()
    home.resize(800,800)
    home.show()

    sys.exit(app.exec())