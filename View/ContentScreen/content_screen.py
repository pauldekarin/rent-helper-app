import json
from typing import Union

from PyQt6.QtWebEngineWidgets import QWebEngineView

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import (
    QCloseEvent,
    QPaintEvent,
    QPixmap,
    QColor,
    QIcon
)
from PyQt6.QtCore import (
    Qt,
    QVariantAnimation,
    QPropertyAnimation,
    QTimer,
    QSize,
    QEvent,
    pyqtSignal,
    pyqtSlot,
    QTimer,
)
from PyQt6.QtWidgets import (
    QWidget,
    QSizePolicy,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
)

from View.Components.Filter.filter import Filter
from View.Components.Cards.cards import Cards

from Utility.style import Style,Theme,Icons, Metrics
from Utility.observer import Observer
from Utility.path import Path


class BadgeIcon(QWidget):
    released = pyqtSignal()

    _enabled = False
    _isBadged = False
    _radius = 7.5

    @property
    def isBadged(self):
        return self._isBadged
    @isBadged.setter
    def isBadged(self, badged):
        if badged != self._isBadged:
            self._isBadged = badged
            self.update()
    @property
    def enabled(self):
        return self._enabled
    @enabled.setter
    def enabled(self, val):
        self._enabled = val
        self._anim.stop()

        self._anim.setDuration(300)
        self._anim.setStartValue(self._anim.currentValue())   
        self._anim.setEndValue(100 if self._enabled else 0)

        self._anim.start()


    def setEnabled(self, enabled: bool) -> None:
        if enabled != self._enabled:
            self.enabled = enabled


    def setHoverAnimationSettings(self, forward = True):
        self._anim.stop()
        self._anim.setDuration(500)
        self._anim.setStartValue(self._anim.currentValue())
        self._anim.setEndValue(50 if forward else 0)

    def __init__(self,icon:QIcon or QPixmap, parent: QWidget or None = None) -> None:
        super().__init__(parent)

        self._badge = QWidget(self)
        self._badge.setFixedSize(16,16)
        
        self.t = 0
        self._anim = QVariantAnimation(
            startValue = 0,
            endValue = 100,
            valueChanged = self.onChangedState,
            duration = 150,
            easingCurve = QtCore.QEasingCurve.Type.InOutCirc
        )
        self.icon = icon
        
        self.setContentsMargins(
            Style.shadowXOffset/2,
            Style.shadowXOffset/2,
            Style.shadowXOffset/2,
            Style.shadowYOffset)
        
        self.setFixedSize(self.icon.size() + QSize(self._badge.width()/2, self._badge.height()/2) 
                          + QSize(
                                self.contentsMargins().left() + self.contentsMargins().right(),
                                self.contentsMargins().top() + self.contentsMargins().bottom()
                          ))
    
    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent or None) -> None:
        self.released.emit()

        return super().mouseReleaseEvent(a0)
    
    def enterEvent(self, event: QtGui.QEnterEvent or None) -> None:
        if not self.enabled:
            self.setHoverAnimationSettings(forward=True)
            
            self._anim.start()

        return super().enterEvent(event)

    def leaveEvent(self, a0: QEvent or None) -> None:
        if not self.enabled:
            self.setHoverAnimationSettings(forward=False)

            self._anim.start()
        return super().leaveEvent(a0)
    
    
    def showBadge(self):
        self.isBadged = True

    def hideBadge(self):
        self.isBadged = False

    def onChangedState(self, perc):
        self.t = perc/100
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent or None) -> None:
        #initialize painter
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        #calculate bounding rect of icon (remove half size of badge)
        rect = self.rect()
        rect.setWidth(rect.width() - self._badge.width()/2)
        rect.setHeight(rect.height() - self._badge.height()/2)
        rect.moveCenter(self.rect().center())

        #clip path from bounding rect with border radius
        clipPath = QtGui.QPainterPath()
        clipPath.addRoundedRect(rect.toRectF(), self._radius,self._radius)

        painter.setClipPath(clipPath)

        #Gradient animation border on hover or press events
        if self.t != 1:
            painter.setBrush(QColor(Theme.shadow))
            painter.drawRect(self.rect())
        
        if self.t != 0:
            rect = self.rect()
            rect.setHeight(rect.height() * self.t)

            painter.setBrush(QColor(Theme.secondaryColor))
            painter.drawRect(rect)

        
        #clip path for icon drawing
        clipPath = QtGui.QPainterPath()
        clipPath.addRoundedRect(
            self.contentsMargins().left() + self._badge.width()/4, 
            self.contentsMargins().top() + self._badge.height()/4, 
            self.icon.width(), 
            self.icon.height(), self._radius,self._radius)

        painter.setClipPath(clipPath)

        #colored or grayscaled image in case of enabled
        if self.enabled:
            painter.drawPixmap(
                clipPath.boundingRect().toRect(), 
                self.icon)
        else:
            painter.drawPixmap(
                clipPath.boundingRect().toRect(), 
                QPixmap.fromImage(
                    self.icon.toImage().convertedTo(QtGui.QImage.Format.Format_Grayscale8)
                    )
            )
        
        #draw badge
        if self._isBadged:
            clipPath = QtGui.QPainterPath()
            clipPath.addRect(self.rect().toRectF())

            painter.setClipPath(clipPath)

            badge = self._badge.rect()
            badge.moveTopRight(self.rect().topRight())

            painter.setBrush(QColor('#EF6262'))
            painter.drawEllipse(badge)

        return super().paintEvent(event)


class Platform(QtWidgets.QStackedWidget):
    class EmptyView(QWidget):
        def __init__(self, parent: QWidget or None = None) -> None:
            super().__init__(parent)

            layout = QVBoxLayout(self)

            label = QLabel('Кажется объявлений нет')
            label.setStyleSheet(f'font-size:{Metrics.h1};font-weight:900')

            layout.addWidget(label)

    class SplashView(QWidget):
        def __init__(self, parent: QWidget or None = None) -> None:
            super().__init__(parent)

            layout = QVBoxLayout(self)

            label = QLabel('Ждем...')

            layout.addWidget(label)

    class WebView(QWidget):
        back = pyqtSignal()

        def __init__(self, parent: QWidget or None = None) -> None:
            super().__init__(parent)

            layout = QtWidgets.QStackedLayout(self)
            layout.setStackingMode(QtWidgets.QStackedLayout.StackingMode.StackAll)

            self._view = QWebEngineView()
            
            self._back = QPushButton()
            self._back.setIcon(QtGui.QIcon(Icons().back))
            self._back.setIconSize(QSize(48,48))
            self._back.setFixedSize(self._back.iconSize())
            self._back.setCheckable(False)
            self._back.setStyleSheet(
                '''
                    QPushButton{{
                        background:{primaryColor}
                    }}
                    QPushButton:hover{{
                        background:{secondaryColor}
                    }}
                '''.format(
                        primaryColor = Theme.primaryColor,
                        secondaryColor = Theme.secondaryColor
                )
            )
            self._back.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed))
            self._back.clicked.connect(self.close)

            layout.addWidget(self._back)
            layout.addWidget(self._view)

        @pyqtSlot()
        def close(self):
            self.back.emit()
            self._view.setHtml('')
            
        def setUrl(self, url:Union[str, QtCore.QUrl]):
            
            self._view.load(QtCore.QUrl(url))
            


    class Type:
        Cards = 0x01
        Empty = 0x02
        Splash = 0x03
        Web = 0x04

    _type = Type.Splash

    @property
    def type(self):
        return self._type
    

    def __init__(self, cards:Cards, parent:QWidget = None) -> None:
        super(Platform, self).__init__(parent=parent)

        self._cards = cards
        self._empty = self.EmptyView()
        self._splash = self.SplashView()
        self._web = self.WebView()
        self._web.back.connect(self.show)

        self.addWidget(self._cards)
        self.addWidget(self._empty)
        self.addWidget(self._splash)
        self.addWidget(self._web)

    def show(self):
        self.setCurrentWidget(self._cards)
        self._type = self.Type.Cards

    def empty(self):
        self.setCurrentWidget(self._empty)
        self._type = self.Type.Empty

    def splash(self):
        self.setCurrentWidget(self._splash)
        self._type = self.Type.Splash
    def web(self, url:str):
        self._web.setUrl(QtCore.QUrl(url))
        self.setCurrentWidget(self._web)

    def instance(self):
        return self._cards
    
class ContentScreenView(QWidget, Observer):
    goToMainThread = pyqtSignal(Observer.ObserverEvent,dict)

    currentPlatform = ''

    def __init__(self, parent: QWidget or None = None, model:object = None, controller:object = None) -> None:
        super().__init__(parent)
        self.goToMainThread.connect(self.mainThread)
    
        self.model = model
        self.controller = controller
        self.cardsManager = QtWidgets.QStackedWidget()
        
        self.model.add_observer(self)

        self.setStyleSheet(
            '''    
                #quantity{{
                    font-weight:900;
                    font-size:{fontSize}
                }}
            '''.format(
                    fontSize = Metrics.h2
            )
        )
        ##Main Layout

        hLayout = QHBoxLayout(self)
        hLayout.setContentsMargins(0,0,0,0)

        hLayout.setSpacing(0)

        ##Advertisments content

        #Counter of ads
        vLayout = QVBoxLayout()
        vLayout.setContentsMargins(
            0,0,0,0
        )
        vLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)


        self.navLayout = QHBoxLayout()
        self.navLayout.setContentsMargins(0,0,0,0)
        self.navLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.navLayout.setSpacing(8)

        self.quantityLabel = QLabel()
        self.quantityLabel.setAccessibleName('Объявления')
        self.quantityLabel.setObjectName('quantity')
        self.quantityLabel.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Maximum,QSizePolicy.Policy.Maximum))

        self.updateQuantity(0)

        self.navLayout.addWidget(self.quantityLabel, alignment=Qt.AlignmentFlag.AlignLeft)

        #platforms switchers
        with open(Path.json('platforms.json')) as f_in:
            for plName, data in json.load(f_in).items():

                cards = Cards()
                
                icon = BadgeIcon(icon = Icons(size = QSize(32,32), color = None).__load__(Path.icon(data['icon'])))
                icon.setAccessibleName(plName)
                icon.released.connect(lambda index = self.cardsManager.count(): self.setCurrentPlatform(index))
                
                cards.viewed.connect(lambda icon = icon: icon.hideBadge)
                cards.hasNew.connect(lambda icon = icon: icon.showBadge)
                cards.comment.connect(lambda text, data : self.onComment(text,data))
                cards.favourite.connect(lambda favourite, data: self.onFavourite(favourite,data))
                cards.pagination.changed.connect(lambda page, plName = plName: self.onPage(page, plName))
                cards.clicked.connect(lambda url, index = self.cardsManager.count(): self.onClick(index, url))

                cards.setAccessibleName(plName)
                cards.countChanged.connect(
                    lambda count, instance = cards: 
                            self.updateQuantity(count) if instance == self.cardsManager.currentWidget().widget(0) else None)

                self.cardsManager.currentChanged.connect(lambda index, badge = icon:
                        badge.setEnabled(True) 
                            if self.cardsManager.currentWidget().widget(0).accessibleName() == badge.accessibleName()
                            else badge.setEnabled(False))
                
         
                platform = Platform(cards)

                self.cardsManager.addWidget(platform)
                
                self.navLayout.addWidget(icon, alignment=Qt.AlignmentFlag.AlignLeft)
        
        vLayout.addLayout(self.navLayout)
       
        vLayout.addWidget(self.cardsManager)

        hLayout.addLayout(vLayout)

        #Closing and opening Filter buttons
        
        openButton = QPushButton(
            icon = QIcon(Icons().filter),
            styleSheet = 'background:none;border:none'
        )
        openButton.setIconSize(QSize(24,24))
        openButton.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum))
        openButton.clicked.connect(self.showFilter)

        closeButton = QPushButton(
            icon = QIcon(Icons().close),
            styleSheet = 'background:transparent;border:none'
        )
        closeButton.setIconSize(QSize(24,24))
        closeButton.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum))
        closeButton.clicked.connect(self.hideFilter)

        #Filter Widget
        self.filter = Filter()
        self.filter.submit.connect(self.onApply)

        #Container where Filter is revealed
        container = QWidget()
        container.setObjectName('filterBar')
        container.setMaximumWidth(320)

        layout = QVBoxLayout(container)
        layout.addWidget(closeButton, alignment= Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.filter)

        hLayout.addWidget(container)

        #Container when Filter is hidden
        bar = QWidget()
        bar.setObjectName('filterBar')
        bar.setMaximumWidth(80)

        layout = QVBoxLayout(bar)
        layout.addWidget(openButton, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        hLayout.addWidget(bar)
        
       #Closing and opening Filter animations
        self._anim_bar = QVariantAnimation(
            startValue = bar.maximumWidth(),
            endValue = 0,
            valueChanged = lambda width, instance = bar: instance.setMaximumWidth(width)
        )

        self._anim_container = QVariantAnimation(
            startValue = container.maximumWidth(),
            endValue = 0,
            valueChanged = lambda width, instance = container: instance.setMaximumWidth(width)
        )

        
        bar.setMaximumWidth(0)
        
        
        
        #Test case
        cards.__test__()
    
    @pyqtSlot(str, str)
    def onPage(self, page, plName):
        for i in range(self.cardsManager.count()):

            cards = self.cardsManager.widget(i).instance()
            

            if cards.accessibleName() == plName:
                cards.clear()

                self.cardsManager.widget(i).splash()

                break

            
        self.controller.onPage(plName, page)

    @pyqtSlot(str,list,list)
    def onApply(self, city:str, price:list, rooms:list)->None:
        self.controller.onApply(city, price, rooms)
    
    @pyqtSlot(str, dict)
    def onComment(self, comment:str, data:dict)->None:
        self.controller.onComment(comment, data)
    @pyqtSlot(bool, dict)
    def onFavourite(self, favourite:bool, data:dict)->None:
        self.controller.onFavourite(favourite, data)

    @pyqtSlot(int, str)
    def onClick(self,index:int, url:str)->None:
        self.cardsManager.widget(index).web(url)

        
    def setFilter(self, city:str, price:list, rooms:list):
        self.filter.set(city = city, price = price, rooms = rooms)
        
    def setCurrentPlatform(self, indicator:Union[str, int]):
        if isinstance(indicator, int):
            if self.cardsManager.currentIndex() != indicator:
                self.cardsManager.setCurrentIndex(indicator)

        elif isinstance(indicator, str):
            for sc_index in range(self.cardsManager.count()):
                screen = self.cardsManager.widget(sc_index)
                if screen.accessibleName() == indicator:
                    self.cardsManager.setCurrentWidget(screen)

        self.updateQuantity(self.cardsManager.currentWidget().instance().count())
    

    def showFilter(self):
        self._anim_bar.setDirection(QPropertyAnimation.Direction.Forward)
        self._anim_container.setDirection(QPropertyAnimation.Direction.Backward)

        self._anim_bar.start()
        QTimer.singleShot(self._anim_bar.duration()/2, lambda *args : self._anim_container.start())
    
    def hideFilter(self):  
        self._anim_container.setDirection(QPropertyAnimation.Direction.Forward)
        self._anim_bar.setDirection(QPropertyAnimation.Direction.Backward)

        self._anim_container.start()
        QTimer.singleShot(self._anim_container.duration()/2, lambda *args : self._anim_bar.start())
    
    def paintEvent(self, event: QPaintEvent or None) -> None:
        painter = QtGui.QPainter(self)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QBrush(QColor('#FFFFFF')))
        painter.drawRect(0,0, self.navLayout.geometry().bottomRight().x(), self.navLayout.geometry().bottomRight().y())
        
        painter.setPen(QtGui.QPen(QColor(Theme.shadow), int(Style.border_width.replace('px',''))))
        painter.drawLine(self.navLayout.geometry().bottomLeft(), self.navLayout.geometry().bottomRight())
        
        return super().paintEvent(event)
    
    @pyqtSlot(int)
    def updateQuantity(self, count):
        self.quantityLabel.setText(
            '{}:{}'.format(self.quantityLabel.accessibleName(), count)
        )

    @pyqtSlot(Observer.ObserverEvent, dict)
    def mainThread(self, event, data):
        
        if event.type() == Observer.ObserverEvent.DATA:
            for i in range(self.cardsManager.count()):
                
                cards = self.cardsManager.widget(i).instance()

                if cards.accessibleName() in data:
                    if data[cards.accessibleName()] == None:
                        
                        self.cardsManager.widget(i).empty()

                    else:
                        if self.cardsManager.widget(i).type != Platform.Type.Cards and self.cardsManager.widget(i).type != Platform.Type.Web:
                            self.cardsManager.widget(i).show()

                        #Remove cards
                        for url in cards.children():
                            if url not in data[cards.accessibleName()]['cards']:
                                cards.remove(url)
                        
                        
                        #Append cards
                        for url, card_data in reversed(data[cards.accessibleName()]['cards'].items()):
                            if not cards.has(url):
                                cards.append(url = url, checked = True, **card_data)
                        
                        #Pagination
                        if data[cards.accessibleName()]['pagination'] != None:
                            if cards.pagination.update(data[cards.accessibleName()]['pagination']['content']):
                                cards.pagination.goTo(data[cards.accessibleName()]['pagination']['current'])
                                if not cards.pagination.isVisible():
                                    cards.pagination.show()
                        else:
                            if cards.pagination.isVisible():
                                cards.pagination.hide()

        elif event.type() == Observer.ObserverEvent.SET_FAVOURITE:
            for i in range(self.cardsManager.count()):
                cards = self.cardsManager.widget(i).findChild(Cards)

                if cards.accessibleName() == data['platform']:
                    cards.setFavourite(url = data['url'], favourite = True)
    

        elif event.type() == Observer.ObserverEvent.REMOVE_FAVOURITE:
            for i in range(self.cardsManager.count()):
                cards = self.cardsManager.widget(i).findChild(Cards)
                
                if cards.accessibleName() == data['platform']:
                    
                    cards.setFavourite(url = data['url'], favourite = False)
        
        elif event.type() == Observer.ObserverEvent.SET_COMMENT:
            for i in range(self.cardsManager.count()):
                cards = self.cardsManager.widget(i).findChild(Cards)

                if data['platform'] == cards.accessibleName():
                    cards.setComment(url = data['url'], comment = data['comment'])


    def model_is_changed(self, event, data):
        self.goToMainThread.emit(event, data)
                    
