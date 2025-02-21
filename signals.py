from PySide6.QtCore import Signal, QObject

class DownloadSignals(QObject):
    progress_update = Signal(str)
    download_finished = Signal()
    download_error = Signal(str)
    