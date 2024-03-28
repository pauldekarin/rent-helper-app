from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
    QSizePolicy
)
from PyQt6.QtCore import (
    pyqtSignal,
    Qt,
    QSize
)

from PyQt6.QtGui import (
    QIcon
)

from Utility.style import Style, Theme, Metrics, Icons

class Pagination(QWidget):
    changed = pyqtSignal(str)
    _currentIndex = 1

    def __init__(self, parent: QWidget or None = None) -> None:
        super().__init__(parent)
        self._currentPage = 1

        self.setStyleSheet(
            '''
                *{{
                    background:transparent;
                }}
                #navArrow{{
                    
                }}
                #navButton{{
                    color:{primaryColor};
                    font-size:{h2};
                    font-weight:900;
                    background:black;
                }}
                #navButton:checked{{
                    color:#AD01F2;
                }}
            '''.format(
                    primaryColor = Theme.primaryColor,
                    h2 = Metrics.h2
            )
        )

        layout = QHBoxLayout(self)
        # layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.la = QPushButton()
        self.la.setIcon(QIcon(Icons(size = QSize(24,24), color = Theme.primaryColor).left_arrow))
        self.la.setIconSize(QSize(24,24))
        self.la.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
        self.la.setObjectName('navArrow')
        self.la.clicked.connect(lambda *args : self.onClick(self._currentIndex - 1))

        self.nav = QHBoxLayout()
        self.nav.setSpacing(4)

        self.ra = QPushButton()
        self.ra.setIcon(QIcon(Icons(color = Theme.primaryColor, size = QSize(24,24)).right_arrow))
        self.ra.setIconSize(QSize(24,24))
        self.ra.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
        self.ra.setObjectName('navArrow')
        self.ra.setCheckable(True)

        self.ra.clicked.connect(lambda *args : self.onClick(self._currentIndex + 1))

        layout.addWidget(self.la)
        layout.addLayout(self.nav)
        layout.addWidget(self.ra)

        self.hide()

    def currentPage(self):
        return self._currentPage
    
        
    def update(self, pages:list):
        if pages:
            if not self.isVisible():
                self.show()

            while self.nav.count():
                child = self.nav.takeAt(0)

                if child.widget():
                    child.widget().deleteLater()
            
            for index, page in enumerate(pages):
                w = QPushButton()
                w.setText(page)
                w.setObjectName('navButton')
                w.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed))
                if page.isdigit():
                    w.setCheckable(True) 
                    w.clicked.connect(lambda checked, instance = w, index = index : self.onClick(index) if index != self._currentIndex else instance.setChecked(True))

                else:
                    w.setCheckable(False)
                    w.setDisabled(True)

                self.nav.addWidget(w)

            return True
        else:
            if self.isVisible():
                self.hide()

            return False
    
    def onClick(self, index):
        self.changed.emit(self.nav.itemAt(index).widget().text())
    def goTo(self, page) -> bool:
        
        

        if page == '1':
            self.la.setDisabled(True)
            self.ra.setEnabled(True)
        
        elif page == str(self.nav.count()):
            self.la.setEnabled(True)
            self.ra.setDisabled(True)
        else:
            self.la.setEnabled(True)
            self.ra.setEnabled(True)

        for i in range(self.nav.count()):
            btn = self.nav.itemAt(i).widget()

            if btn.text() == page:
                btn.setChecked(True)
                self._currentIndex = i

            else:
                btn.setChecked(False)
        
        return True
        
        