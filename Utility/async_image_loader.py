from PyQt6 import QtNetwork
from PyQt6.QtGui import (
    QPixmap
)
from PyQt6.QtCore import (
    pyqtSignal,
    QUrl,
    QObject
)
class AsyncImageLoader(QObject):
    progress = pyqtSignal()
    complete = pyqtSignal(QPixmap)
    failed = pyqtSignal()
    
    def handler(self, response:QtNetwork.QNetworkReply):
        if response.error() == QtNetwork.QNetworkReply.NetworkError.NoError:
            pixmap = QPixmap()
            pixmap.loadFromData(response.readAll())

            self.complete.emit(pixmap)

        else:
            self.failed.emit()

    def __init__(self, url) -> None:
        super().__init__()
        req = QtNetwork.QNetworkRequest(QUrl(url))

        self.nam = QtNetwork.QNetworkAccessManager()
        self.nam.finished.connect(self.handler)
        self.nam.get(req)