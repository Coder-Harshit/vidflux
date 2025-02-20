from PySide6 import QtWidgets
from widgets.queue import DownloadQueue
from utils import validateURL

class HomeWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        rightHalf = None
        leftHalf = None

        self.url_bar = QtWidgets.QLineEdit('Enter URL Here')
        self.url_bar.returnPressed.connect(self.search_url)

        self.search_btn = QtWidgets.QPushButton("search")
        self.search_btn.clicked.connect(self.search_url)

        l1 = QtWidgets.QHBoxLayout()    # vertical layout
        l1.addWidget(self.url_bar)
        l1.addWidget(self.search_btn)

        self.settings_btn = QtWidgets.QPushButton("SETTINGS")
        self.settings_btn.clicked.connect(lambda : print("clicked"))

        l2 = QtWidgets.QVBoxLayout()
        l2.addWidget(self.settings_btn)
        l2.addLayout(l1)

        self.setLayout(l2)        

    def search_url(self):
        print(validateURL.validate(self.url_bar.text())) 
