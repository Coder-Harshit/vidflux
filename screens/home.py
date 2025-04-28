from email.mime import audio
import select
from PySide6 import QtWidgets
from pandas import DataFrame
from widgets.queue import DownloadQueue
from utils import validateURL
from utils.ytdlp import DownloadWorker
import sys
import threading
from signals import DownloadSignals
from screens.download_finish import FinishDialog
from screens.format_selection import FormatSelector

class HomeWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.output_fmt = None

        self.signals = DownloadSignals()

        rightHalf = None
        leftHalf = None


        self.settings_btn = QtWidgets.QPushButton("SETTINGS")
        self.settings_btn.clicked.connect(lambda : print("settings btn clicked"))

        self.url_bar = QtWidgets.QLineEdit('Enter URL Here')
        self.url_bar.returnPressed.connect(self.search_url)

        self.search_btn = QtWidgets.QPushButton("search")
        self.search_btn.clicked.connect(self.search_url)

        self.log_viewer = QtWidgets.QPlainTextEdit("Logs go here....")
        self.log_viewer.setReadOnly(True)

        self.clear_logs_btn = QtWidgets.QPushButton("Clear Logs")
        self.clear_logs_btn.clicked.connect(self.empty_logs)
        self.save_logs_btn = QtWidgets.QPushButton("Save Logs")
        self.save_logs_btn.clicked.connect(self.save_logs)


        l1 = QtWidgets.QHBoxLayout()    # vertical layout
        l1.addWidget(self.url_bar)
        l1.addWidget(self.search_btn)

        l3 = QtWidgets.QVBoxLayout()
        l3.addWidget(self.log_viewer)

        l4 = QtWidgets.QHBoxLayout()
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
            self.worker.signals.download_finished.connect(self.finished_modal)
            self.worker.signals.formats_listed.connect(self.open_format_selector)
            self.download_dir = QtWidgets.QFileDialog.getExistingDirectory(self,("Open Directory"),
                                                                      options=QtWidgets.QFileDialog.Options(
                                                                        QtWidgets.QFileDialog.ShowDirsOnly  
                                                                      )
            )
            # self.worker_thread = threading.Thread(target=self.worker.download, args=(url,download_dir,self.output_fmt))
            self.worker_thread = threading.Thread(target=self.worker.formatSelection, args=(url,))
            self.worker_thread.start()

    def empty_logs(self):
        self.log_viewer.clear()

    def save_logs(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, caption="Save File", dir='logs/')
        print(filename)
        if filename:
            with open(filename, 'w') as file:
                file.write(self.log_viewer.toPlainText())
        else: 
            print("OPERATION TERMINATED")
   
    def open_format_selector(self, formats: DataFrame):
        popup = FormatSelector(self, formats)
        popup.exec()

        if popup.result() == QtWidgets.QDialog.Accepted:
            selected_formats = popup.get_selected_formats()
            print(selected_formats)
            # if selected_formats:
            #     self.output_fmt = selected_formats
            #     print("Selected formats:", self.output_fmt)
            audio_id = selected_formats.get('audio')
            video_id = selected_formats.get('video')

            if audio_id and video_id:
                ydl_format_string = f"{audio_id}+{video_id}"
            elif audio_id:
                ydl_format_string = audio_id
            elif video_id:
                ydl_format_string = video_id
            else:
                print("No formats selected.")
                return
            print("YDL format string:", ydl_format_string)
        if popup.result() == QtWidgets.QDialog.Rejected:
            # TODO
            # instead of exit clear the url
            exit()

        self.downloader_thread = threading.Thread(
            target=self.worker.download,
            args=(self.url_bar.text(), self.download_dir, ydl_format_string)
        )
        self.downloader_thread.start()
        


    def finished_modal(self,fileurl):
        # QtWidgets.QMessageBox.information(self, "Download Finished", "Download Completed Successfully", QtWidgets.QMessageBox.Ok)
        popup = FinishDialog(self,fileurl)
        popup.exec()

    def write_log(self,text):
        self.log_viewer.appendPlainText(text)
    
    def clear_log(self):
        self.log_viewer.setPlainText()
