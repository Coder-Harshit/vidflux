from PySide6 import QtWidgets, QtCore
import subprocess
import sys


class FinishDialog(QtWidgets.QDialog):
    def __init__(self, parent, file_path):
        super().__init__()
        self.setWindowTitle("Download Finished")
        self.setGeometry(100, 100, 300, 200)
        self.setModal(True)

        self.fileurl = file_path
        self.filename_with_ext = file_path.split("/")[-1]
        self.filename = self.filename_with_ext.split(".")[0]

        self.label = QtWidgets.QLabel(f"\"{self.filename_with_ext}\" finished Downloading! :)", self)
        # self.label.setGeometry(50, 50, 200, 50)

        self.ok_button = QtWidgets.QPushButton("OK", self)
        self.ok_button.setGeometry(100, 120, 100, 30)
        self.ok_button.clicked.connect(self.accept)

        self.open_button = QtWidgets.QPushButton("Play", self)
        self.open_button.setGeometry(100, 160, 100, 30)
        self.open_button.clicked.connect(self.play_file)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.ok_button)
        btn_layout.addWidget(self.open_button)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

    def play_file(self):
        if self.fileurl:
            print(self.fileurl)
            if sys.platform.startswith("linux"):
                # LINUX
                subprocess.run(["xdg-open", self.fileurl])
            elif sys.platform == "darwin":
                # MAC OS
                subprocess.run(["open", self.fileurl])
            elif sys.platform.startswith("win"):
                # WINDOWS
                subprocess.run(["start", "", self.fileurl], shell=True)
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "Unsupported OS.")
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "File not found.")
