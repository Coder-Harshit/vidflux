from PySide6 import QtWidgets
from widgets.queue import DownloadQueue
from utils import validateURL
from utils.ytdlp import download
import sys

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

        self.log_viewer = QtWidgets.QPlainTextEdit("Logs go here....")
        self.log_viewer.setReadOnly(True)

        l3 = QtWidgets.QVBoxLayout()
        l3.addWidget(self.log_viewer)

        l4 = QtWidgets.QHBoxLayout()
        self.clear_logs_btn = QtWidgets.QPushButton("Clear Logs")
        self.clear_logs_btn.clicked.connect(self.empty_logs)
        self.save_logs_btn = QtWidgets.QPushButton("Save Logs")
        self.save_logs_btn.clicked.connect(self.save_logs)
        l4.addWidget(self.clear_logs_btn)
        l4.addWidget(self.save_logs_btn)

        l3.addLayout(l4)

        l2 = QtWidgets.QVBoxLayout()
        l2.addWidget(self.settings_btn)
        l2.addLayout(l1)
        l2.addLayout(l3)
        self.setLayout(l2)       

        sys.stdout = self.LogOutput(self.log_viewer)

    def search_url(self):
        url:str = self.url_bar.text()
        if not validateURL.validate(url):
            print("Check input URL")
        else: 
            download(url,console=self.log_viewer)

    def empty_logs(self):
        self.log_viewer.clear()

    def save_logs(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, caption="Save File", dir='logs')
        print(filename)
        if filename:
            with open(filename,'w') as file:
                print(self.log_viewer.text(),file=file)
        else: 
            print("OPERATION TERMINATED")

    class LogOutput:
        def __init__(self,console):
            self.console = console
        
        def write(self,text):
            self.console.appendPlainText(text)
        
        def clear(self):
            self.console.setPlainText("Logs go here....")

        def flush(self):
            pass
