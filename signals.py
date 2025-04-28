from PySide6.QtCore import Signal, QObject
from pandas import DataFrame

class DownloadSignals(QObject):
    progress_update = Signal(str)
    download_finished = Signal(str)
    download_error = Signal(str)
    formats_listed = Signal(DataFrame)
    