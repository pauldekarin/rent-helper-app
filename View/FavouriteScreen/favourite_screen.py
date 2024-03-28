

from PyQt6.QtGui import (
    QPaintEvent,
    QPainter,
    QPixmap
)
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
)
from PyQt6.QtCore import (
    QEvent,
    QObject,
    Qt
)

from View.Components.Cards.cards import Cards
from Utility.observer import Observer
from Utility.style import Style,Metrics,Icons,Theme
from Utility.path import Path

class FavouriteScreenView(QWidget, Observer):
    def __init__(self, parent: QWidget or None = None, model:object = None, controller:object = None) -> None:
        super().__init__(parent)

        self.setStyleSheet(
            '''
                #title{{
                    font-weight:900;
                    font-size:{h1};
                    color:{primaryColor}
                }}
            '''.format(
                h1 = Metrics.h1,
                primaryColor = Theme.primaryColor
            )
        )
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.title = QLabel(
            objectName = 'title'
        )
    
        layout.addWidget(self.title)

        self.cards = Cards()
        self.cards.favourite.connect(self.onFavourite)
        self.cards.comment.connect(self.onComment)
        self.cards.countChanged.connect(self.updateQuantity)
        
        self.image = QPixmap(Path.image('favourite_screen_splash.png'))

        layout.addWidget(self.cards)

        self.model = model
        self.model.add_observer(self)
        
        self.controller  = controller
      
    def paintEvent(self, a0: QPaintEvent or None) -> None:
        if self.cards.count() == 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.NonCosmeticBrushPatterns)

            sz = max(self.width(), self.height())
            pixmap = self.image.scaled(
                sz - 48,
                sz,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            painter.drawPixmap(self.rect().center() - pixmap.rect().center(),pixmap)
            painter.end()

        return super().paintEvent(a0)
    
    def updateQuantity(self, count):
        if count > 0:
            self.title.setText('Любимое : {}'.format(count))
        else:
            self.title.setText('')

    def onFavourite(self, favourite, data:dict):
        self.cards.remove(data['url'])
            
        self.controller.onFavourite(favourite, data)
    
    def onComment(self, comment, data):
        self.controller.onComment(comment, data)
        
    def model_is_changed(self, event:Observer.ObserverEvent, data:dict):
        
        if event.type() == Observer.ObserverEvent.SET_FAVOURITE:
            self.cards.append(**data)

        elif event.type() == Observer.ObserverEvent.REMOVE_FAVOURITE:
            self.cards.remove(url = data['url'])
        
        elif event.type() == Observer.ObserverEvent.SET_COMMENT:
            self.cards.setComment(url = data['url'], comment = data['comment'])
            


