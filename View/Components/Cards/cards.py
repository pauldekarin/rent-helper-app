from PyQt6 import QtWidgets, QtCore, QtGui, QtNetwork
from PyQt6.QtWebEngineWidgets import QWebEngineView

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QScrollArea
)
from PyQt6.QtGui import (
    QMouseEvent,
    QPixmap,
)
from PyQt6.QtCore import (
    QEvent,
    Qt,
    pyqtSignal,
    QObject,    
    QVariantAnimation,
    QSize
)

from Utility.style import Metrics,Style, Theme,Icons
from Utility.async_image_loader import AsyncImageLoader
from Utility.path import Path

from View.Components.Comment.comment import Comment
from View.Components.Pagination.pagination import Pagination
from View.Components.Widgets.widgets import Widget



    
class CardWidget(QWidget):
    _checked = bool(False)
    
    checked = pyqtSignal()
    clicked = pyqtSignal()

    def isChecked(self):
        return self._checked
     
    def __init__(self, 
                 url:str = '',
                 img_sources:list = [],
                 title:str = '',
                 price:str or list = '',
                 subway_name:str = '',
                 subway_time:str = '',
                 meta:str = '',
                 address:str = '',
                 description:str = '',
                 time:str = '',
                 platform:str = '',
                 favourite:bool = False,
                 comment:str = '',
                 checked:bool = False) -> None:
        super(CardWidget, self).__init__()

        self.url = url
        self.img_sources = img_sources
        self.title = title
        self.price = price
        self.subway_name = subway_name
        self.subway_time = subway_time
        self.meta = meta
        self.address = address
        self.description = description.replace('\n','')
        self.time = time
        self.platform = platform
        
        self.imageLoader = None
        

        self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum))
        self.setStyleSheet(
            '''
                #notification{{
                    font-size:{h1};
                    color:{primaryColor};
                    font-weight:900;
                }}
                #title{{
                    font-weight:900;
                    font-size:{h1}
                }}
                #price{{
                    font-weight:900;
                    font-size:{h1};
                    color:{primaryColor}
                }}
                #meta{{
                    font-weight:900;
                    font-size:{p};
                    color:{secondaryTextColor};
                }}
                #address{{
                    font-size:12px;
                    color:#468B97
                }}
                #description{{
                }}
                #subway{{
                    font-weight:900;
                    font-size:{p};
                    color:{secondaryTextColor};
                }}
            '''.format(
                    secondaryTextColor = Theme.secondaryTextColor,
                    p = Metrics.p,
                    h2 = Metrics.h2,
                    h1 = Metrics.h1,
                    primaryColor = Theme.primaryColor,
                    shadow = Theme.shadow,
                    borderRadius = Style.border_radius,
                    borderWidth = Style.border_width,
                    window = Theme.window
            )
        )
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(0,0,0,0)
        

        if checked:
            self._checked = True
        else:
            self.notification = QLabel(
                text = 'NEW!',
                objectName = 'notification',
                alignment = Qt.AlignmentFlag.AlignRight,
            )
            self.notification.setContentsMargins(0,0,int(Style.border_radius),0)

            mainLayout.addWidget(self.notification)

        
        self.content = Widget(objClass=QWidget)
        self.content.instance().setStyleSheet(f'background:{Theme.window}')
        self.content.installEventFilter(self)

        self.content.setAccessibleName('content')
        self.content.setFixedHeight(280)
        self.content.setShadowFill(True)
        
        hBoxLayout = QHBoxLayout()
        hBoxLayout.setContentsMargins(8,8,8,8)
        
        
        self.image = QLabel()
        self.image.setFixedSize(QSize(200 - 16,self.content.height() - 32))
        self.image.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        )
        self.image.installEventFilter(self)

        pixmap = QPixmap(self.image.size())
        print(pixmap.isNull())
        pixmap.fill(QtGui.QColor('transparent'))

        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QBrush(
                    QPixmap(Path.image('card_splash.jpg')).scaled(
                                        self.image.size(), 
                                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                        Qt.TransformationMode.SmoothTransformation
                                                    )
                                    )
                        )
        
        painter.drawRoundedRect(
            self.image.rect().toRectF().adjusted(0,0,100,0), 
            int(Style.border_radius),
            int(Style.border_radius))

        painter.end()

        self.image.setPixmap(pixmap)

        if len(self.img_sources):
            self.imageLoader = AsyncImageLoader(self.img_sources[0])
            self.imageLoader.complete.connect(self.onImageLoad)
            
        
        hBoxLayout.addWidget(self.image, alignment=Qt.AlignmentFlag.AlignTop)

        textLayout = QVBoxLayout()
        textLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        hLayout = QtWidgets.QHBoxLayout()
        title = QLabel(
            text = self.title,
            objectName = 'title',
            wordWrap = True,
            sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum),
            alignment = Qt.AlignmentFlag.AlignTop
        )

        self.favouriteButton = QtWidgets.QPushButton()
        self.favouriteButton.setIcon(QtGui.QIcon(Icons(color = None).favourite))
        self.favouriteButton.setIconSize(QtCore.QSize(32,32).grownBy(QtCore.QMargins(8,8,8,8)))
        self.favouriteButton.setFixedSize(self.favouriteButton.iconSize())
        self.favouriteButton.setStyleSheet(
            '''
                QPushButton{{
                    border-radius:{borderRadius};
                    border-top:1px solid white;
                    border-left:1px solid white;
                    border-right:1px solid black;
                    border-bottom:1px solid black;
                }}
                QPushButton:hover{{
                    border-top:1px solid black;
                    border-left:1px solid black;
                    border-right:1px solid white;
                    border-bottom:1px solid white;
                }}
                QPushButton:checked{{
                    border-top:1px solid {color};
                    border-left:1px solid {color};
                    border-right:1px solid black;
                    border-bottom:1px solid black;
                }}
            '''.format(
                    color = Theme.secondaryColor,
                    borderRadius = Style.border_radius
            )
        )
        self.favouriteButton.setCheckable(True)
        self.favouriteButton.setChecked(favourite)

        if not favourite : self.favouriteButton.hide()
   

        hLayout.addWidget(title,stretch=2)
        hLayout.addWidget(self.favouriteButton, stretch=1)

        textLayout.addLayout(hLayout)
        
        textLayout.addWidget(QLabel(
            text = self.price,
            objectName = 'price',
            wordWrap = True,
            sizePolicy = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed),
            alignment = Qt.AlignmentFlag.AlignTop
        ))
        textLayout.addWidget(QLabel(
            text = self.meta,
            objectName = 'meta',
            wordWrap = True,
            sizePolicy = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed),
            alignment = Qt.AlignmentFlag.AlignTop
        ))
        textLayout.addWidget(QLabel(
            text = self.address,
            objectName = 'address',
            wordWrap = True,
            sizePolicy = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed),
            alignment = Qt.AlignmentFlag.AlignTop
        ))
        if self.subway_name != '':
            l = QHBoxLayout()
            l.setAlignment(Qt.AlignmentFlag.AlignLeft)
            l.addWidget(QLabel(
                text = self.subway_name,
                wordWrap = True,
                objectName = 'subway'
            ))
            l.addWidget(QLabel(
                text = self.subway_time,
                wordWrap = True,
                objectName = 'subway'
            ))
            textLayout.addLayout(l)

        textLayout.addWidget(QLabel(
            text = self.description,
            objectName = 'description',
            wordWrap = True,
            alignment = Qt.AlignmentFlag.AlignAbsolute,
            sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        ))
        textLayout.addWidget(QLabel(
            text = self.time,
            objectName = 'time',
            wordWrap = True,
        ), alignment = Qt.AlignmentFlag.AlignRight)

        hBoxLayout.addLayout(textLayout)

        self.content.instance().setLayout(hBoxLayout)
    
        mainLayout.addWidget(self.content)
        
        
        self.comment = Comment()
        self.comment.setSizePolicy(QSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed
        ))
        self.comment.textEdit.setSizePolicy(QSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed
        ))
        if comment != None:
            self.comment.textEdit.blockSignals(True)
            self.comment.textEdit.setText(str(comment))
            self.comment.textEdit.blockSignals(False)

        self.comment.setMinimumHeight(100)
        
        mainLayout.addWidget(self.comment)
    

    def __del__(self):
        if self.imageLoader:
            self.imageLoader.disconnect()

    def onImageLoad(self, pixmap:QPixmap):
        try:
            if not pixmap.isNull():
                self.image.setPixmap(
                    pixmap.scaled(
                        self.image.size(),
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation))
        except Exception as e:
            pass

    def get(self):
        return {
                'url':self.url,
                
                'img_sources':self.img_sources,
                'title':self.title,
                
                'subway_name':self.subway_name,
                'subway_time':self.subway_time,
                
                'address':self.address,
                'price':self.price,
                'meta':self.meta,
                'description':self.description,

                'time':self.time,
                'platform':self.platform,

                'comment':self.comment.textEdit.toPlainText(),
                'favourite':self.favouriteButton.isChecked()
            
            }

    def eventFilter(self, obj: QObject or None, event: QEvent or None) -> bool:

        if obj == self.image and event.type() == QEvent.Type.Paint:
            painter = QtGui.QPainter()
            painter.begin(obj)
            clipPath = QtGui.QPainterPath()
            clipPath.addRoundedRect(self.image.rect().adjusted(0,0,100,0).toRectF(),int(Style.border_radius),int(Style.border_radius))
            painter.setClipPath(clipPath)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPixmap(self.image.rect(), self.image.pixmap(), self.image.rect())
            painter.drawRect(obj.rect())
            painter.end()

            return True
        elif obj == self.content and event.type() == QEvent.Type.MouseButtonRelease:
            self.clicked.emit()

        return super().eventFilter(obj, event)
    
    
    def enterEvent(self, event: QtGui.QEnterEvent or None) -> None:
        if not self._checked:
            self._checked = True
            self.checked.emit()

            self.layout().removeWidget(self.notification)
            self.notification.deleteLater()

        if not self.favouriteButton.isChecked():
            self.favouriteButton.show()

        return super().enterEvent(event)

    def leaveEvent(self, a0: QEvent or None) -> None:
        if not self.favouriteButton.isChecked():
            self.favouriteButton.hide()

        return super().leaveEvent(a0)
   
  
class Cards(QScrollArea):
    countChanged = pyqtSignal(int)
    hasNew = pyqtSignal()
    viewed = pyqtSignal()
    add = pyqtSignal(str, bool,dict)
    clicked = pyqtSignal(str)

    favourite = pyqtSignal(bool, dict)
    comment = pyqtSignal(str, dict)

    def __init__(self, parent: QWidget or None = None) -> None:
        super().__init__(parent)
        self.add.connect(self.append)
 
        widget = QWidget()
        self.setWidget(widget)

        layout = QVBoxLayout()

        self.container = QVBoxLayout()
        self.container.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.container.setContentsMargins(0,0,0,0)

        
        layout.addLayout(self.container)

        self.pagination = Pagination()
        
        layout.addWidget(self.pagination)

        widget.setLayout(layout)

        #Styling
        self.setStyleSheet('background:transparent')

        #Scroll Bars
        self.horizontalScrollBar().setEnabled(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.verticalScrollBar().setStyleSheet("QScrollBar {width:0px}")
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        
        #Settings
        self.setWidgetResizable(True)
        self.setContentsMargins(0,0,0,0)
    
   
   
    def append(self, 
               url:str = '', 
               comment:str = None, 
               favourite:bool = False, 
               checked:bool = False, 
               **kwargs):
        card = CardWidget(url=url,
                           favourite=favourite, 
                           comment=comment, 
                           checked=checked,
                           **kwargs)
        card.comment.textEdit.textChanged.connect(
            lambda instance = card.comment.textEdit, card = card : self.comment.emit(instance.toPlainText(), card.get()))
        card.favouriteButton.clicked.connect(
            lambda favourite, card = card : self.favourite.emit(favourite, card.get())
        )
        card.checked.connect(self.getChecked)
        card.clicked.connect(lambda url = url: self.clicked.emit(url))
        
        self.container.insertWidget(0, card)
        
        if not checked:
            self.hasNew.emit()
        
        self.countChanged.emit(self.count())


    def clear(self):
        for i in range(self.count()):
            item = self.container.itemAt(i)

            if item:
                self.container.removeWidget(item.widget())
                item.widget().deleteLater()

    def has(self, url):
        for i in range(self.count()):
            item = self.container.itemAt(i).widget()

            if item.url == url:
                return True
            
        return False
    
    def children(self):
        return [self.container.itemAt(i).widget().url for i in range(self.container.count())]
    
    def remove(self, url):
        for i in range(self.count()):
            item = self.container.itemAt(i)
            if item:
                if item.widget().url == url:
                    self.container.removeItem(item)
                    item.widget().deleteLater()

                    self.countChanged.emit(self.count())

    def setComment(self, url, comment):
        for i in range(self.count()):
            card = self.container.itemAt(i).widget()

            if card.url == url:
                
                card.comment.textEdit.blockSignals(True)
                card.comment.textEdit.setPlainText(comment)
                card.comment.textEdit.blockSignals(False)

       
    def setFavourite(self, url, favourite):
        for i in range(self.count()):
            card = self.container.itemAt(i).widget()

            if card.url == url:
                card.favouriteButton.setChecked(favourite)
                if favourite:
                    card.favouriteButton.show()
                else:
                    card.favouriteButton.hide()

    def getChecked(self, *args):
        for item in self.widget().children():
            if isinstance(item, CardWidget) and not item.isChecked():
                return self.hasNew.emit()
            
        return self.viewed.emit()
    
    def __test__(self, count = 20,**kwargs):
        for i in range(count):
            kwargs['img_sources'] = Path.image('card_splash.jpg')
            self.append(url = 'https://google.com', **kwargs)

    def count(self):
        return self.container.count()
    
   