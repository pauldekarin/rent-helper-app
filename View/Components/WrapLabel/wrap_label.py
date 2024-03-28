from PyQt6.QtCore import (
    Qt,
    QSize
)

from PyQt6.QtWidgets import (
    QTextEdit,
    QSizePolicy,
)
class WrapLabel(QTextEdit):
    def __init__(self, text='', **kwargs):
        super().__init__(text, **kwargs)
        # self.setStyleSheet('''
        #     WrapLabel {
        #         background:transparent;
        #         border:none;
        #     }
        # ''')
        self.setReadOnly(True)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, 
            QSizePolicy.Policy.Maximum)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.textChanged.connect(self.updateGeometry)

    def minimumSizeHint(self):
        doc = self.document().clone()
        doc.setTextWidth(self.viewport().width())
        height = doc.size().height()
        height += self.frameWidth() * 2
        return QSize(50, height)

    def sizeHint(self):
        return self.minimumSizeHint()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateGeometry()
