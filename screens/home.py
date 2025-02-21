from PySide6 import QtWidgets
from widgets.queue import DownloadQueue
from utils import validateURL
from utils.ytdlp import DownloadWorker
import sys
import threading
from signals import DownloadSignals

class HomeWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()


        self.signals = DownloadSignals()

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

        # sys.stdout = self.log_viewer
        self.worker = None

    def search_url(self):
        url:str = self.url_bar.text()
        if not validateURL.validate(url):
            print("Check input URL")
        else: 
            self.worker = DownloadWorker()
            self.worker.signals.progress_update.connect(self.write_log)
            # self.worker.signals.download_error.connect()
            # self.worker.signals.download_finished.connect()
            self.worker_thread = threading.Thread(target=self.worker.download, args=(url,))
            self.worker_thread.start()

    def empty_logs(self):
        self.log_viewer.clear()

    def save_logs(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, caption="Save File", dir='logs')
        print(filename)
        if filename:
            with open(filename,'w') as file:
                print(self.log_viewer.toPlainText(),file=file)
        else: 
            print("OPERATION TERMINATED")
   
    def write_log(self,text):
        self.log_viewer.appendPlainText(text)
    
    def clear_log(self):
        self.log_viewer.setPlainText()
