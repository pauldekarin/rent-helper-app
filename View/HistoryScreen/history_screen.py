from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QMouseEvent, QPainter, QResizeEvent
from PyQt6.QtWidgets import (
    QGraphicsItem,
    QGraphicsSceneHoverEvent,
    QStyleOptionGraphicsItem,
    QWidget,
)


from Utility.observer import Observer
from Utility.style import Style,Theme,Metrics,Icons
from Utility.date import Date
from Utility.path import Path

class GraphicsRoundedRectItem(QtWidgets.QGraphicsRectItem):
    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()
    
    def __init__(self):
        super().__init__()
        self.setAcceptHoverEvents(True)
        
        self.mousePos = QtCore.QPointF()
    def paint(self, painter: QPainter or None, option: QStyleOptionGraphicsItem or None, widget: QWidget or None = ...) -> None:
        painter.setPen(self.pen())
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.drawRoundedRect(self.rect(), int(Style.border_radius),int(Style.border_radius))
        return 
    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent or None) -> None:
        self.mousePos = event.pos()
        self.update()
        return super().hoverMoveEvent(event)
   
class margin:
        left = 16
        top = 16
        right = 16
        bottom = 16

class GraphicsStackItemGroup(QtWidgets.QGraphicsItemGroup):
    def __init__(self, parent: QGraphicsItem or None = None) -> None:
        super().__init__(parent)
        
        self.spacing = 8
        self.width = 0

    def setSpacing(self, spacing):
        self.spacing = spacing
        self.resize(self.width)

    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()
    
    def resize(self, width):
        self.width = width

        dx = 0
        dy = 0

        for item in self.childItems():
            item.setPos(dx,dy)
            space = item.boundingRect().width() + self.spacing

            if dx + space < width:
                dx += space
            else:
                dx = 0
                dy += item.boundingRect().height() + self.spacing

class HistoryRow(QtWidgets.QGraphicsItemGroup):
    clicked = QtCore.pyqtSignal()

    class Margin:
        left = 16
        top = 16
        right = 16
        bottom = 16
    
    
    def __init__(self, city:str, price:list, rooms:list, time:int or str, parent: QGraphicsItem or None = None) -> None:
        super().__init__(parent)
        self.iconSpacing = 16
        self.iconSpacings = (6,6,6,6)
        self.setAcceptHoverEvents(True)
        self.setAcceptTouchEvents(True)
        self.setAcceptedMouseButtons(Qt.MouseButton.AllButtons)

        self.city = city
        self.price = price
        self.rooms = rooms
        self.time = time
        
        self.setFlag(QtWidgets.QGraphicsItemGroup.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable)

        self.group = QtWidgets.QGraphicsItemGroup()

       #CITY
        icon = QtWidgets.QGraphicsPixmapItem()
        icon.setPixmap(Icons().map)

        text = QtWidgets.QGraphicsTextItem()
        text.setPlainText(city)
        text.setFont(QtGui.QFont(
            QtWidgets.QApplication.font().family(),
            int(Metrics.h2.replace('px','')),
            QtGui.QFont.Weight.Black
        ))
        text.setDefaultTextColor(QtGui.QColor(Theme.secondaryTextColor))
        
        self.group.addToGroup(icon)
        self.group.addToGroup(text)

        
        #PRICE
        icon = QtWidgets.QGraphicsPixmapItem()
        icon.setPixmap(Icons().coins)

        text = QtWidgets.QGraphicsTextItem()
        text.setHtml('от  <font color = "{color}">{priceFrom}₽</font>  до  <font color = "{color}">{priceTo}₽</font'.format(
            color = Theme.primaryColor,
            priceFrom = str(price[0])  if isinstance(price[0],int) or price[0].isdigit() 
                        else '0',
            priceTo = str(price[1]) if (isinstance(price[1],int) and price[1] > 0) or (isinstance(price[1],str) and price[1] != '') 
                        else '∞'
        ))
        text.setFont(QtGui.QFont(
            QtWidgets.QApplication.font().family(),
            int(Metrics.h2.replace('px','')),
            QtGui.QFont.Weight.Black
        ))
        text.setDefaultTextColor(QtGui.QColor(Theme.secondaryTextColor))

        self.group.addToGroup(icon)
        self.group.addToGroup(text)

        #ROOMS
        icon = QtWidgets.QGraphicsPixmapItem()
        icon.setPixmap(Icons().room)
        self.group.addToGroup(icon)

        self.roomsGrid = GraphicsStackItemGroup()

        if len(rooms):
            for room in rooms:
                self.roomsGrid.addToGroup(GraphicsCheckItem(room))
        else:
            self.roomsGrid.addToGroup(GraphicsCheckItem('Все'))

        
        self.roomsGrid.resize(50)

        
        self.group.addToGroup(self.roomsGrid)
        
        
        #TIME
        icon = QtWidgets.QGraphicsPixmapItem()
        icon.setPixmap(Icons().time)

        text = QtWidgets.QGraphicsTextItem()
        text.setPlainText(time)
        text.setFont(QtGui.QFont(
            QtWidgets.QApplication.font().family(),
            int(Metrics.h2.replace('px','')),
            QtGui.QFont.Weight.ExtraLight
        ))
        text.setDefaultTextColor(QtGui.QColor(Theme.secondaryTextColor))

        self.group.addToGroup(icon)
        self.group.addToGroup(text)

        self.height = self.group.childrenBoundingRect().height() + margin.top + margin.bottom
        
        self.border = GraphicsRoundedRectItem()
        self.border.setPen(
            QtGui.QPen(QtGui.QColor(Theme.shadow), 
                       int(Style.border_width.replace('px',''))
                       ))
        self.border.setAcceptHoverEvents(True)
        self.addToGroup(self.border)
        self.addToGroup(self.group)

        self.calculateMinimumWidth()
        self.centeredItems()
        
    
    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent or None) -> None:
        self.border.hoverMoveEvent(event)
        return super().hoverMoveEvent(event)
    
    def centeredItems(self):
        for item in self.group.childItems():
            
            if isinstance(item, QtWidgets.QGraphicsItemGroup):
                itemHeight = item.childrenBoundingRect().height()
            else:
                itemHeight = item.boundingRect().height()

            item.setY(margin.top + (self.group.childrenBoundingRect().height() - itemHeight)/2)
    
    def calculateMinimumWidth(self):
        self.minimumWidth = 0

        for item in self.group.childItems():
            self.minimumWidth += item.childrenBoundingRect().width() if isinstance(item,QtWidgets.QGraphicsItemGroup) else item.boundingRect().width()

            if isinstance(item, QtWidgets.QGraphicsPixmapItem):
                self.minimumWidth += self.iconSpacing

    
    def resize(self, width:int or None = 0):
        self.border.setRect(0,0,width, self.height)

        width = max(self.minimumWidth, width) - margin.left - margin.right

        items = self.group.childItems()
        spacing = (width - self.minimumWidth) / (len(items)/2 - 1) 

        dx = margin.left

        for item in items:
            item.setX(dx)

            dx += item.boundingRect().width()

            if isinstance(item, QtWidgets.QGraphicsPixmapItem):
                dx += self.iconSpacing
            else:
                dx += spacing

    def get(self):
        return {
            'price':self.price,
            'rooms':self.rooms,
            'city':self.city,
        }
    
class GraphicsCheckItem(QtWidgets.QGraphicsItemGroup):
    class margin:
        left = 2
        top = 4
        right = 2
        bottom = 4
        horizontal = left + right
        vertical = bottom + top
    
    def __init__(self,text:str or int = '', parent: QGraphicsItem or None = None) -> None:
        super().__init__(parent)

        self.text = QtWidgets.QGraphicsTextItem(text)

        self.text.setPos(self.margin.left, self.margin.top)
        self.text.setFont(QtGui.QFont(
            QtWidgets.QApplication.font().family(),
            int(Metrics.h2.replace('px','')),
            QtGui.QFont.Weight.Black
        ))
        
        self.border = QtWidgets.QGraphicsRectItem()
        self.border.setPen(QtGui.QPen(QtGui.QColor('transparent')))
        self.border.setBrush(QtGui.QColor('transparent'))
        self.border.setVisible(False)
        self.border.setRect(0,0, self.text.boundingRect().width() + self.margin.horizontal, self.text.boundingRect().height() + self.margin.vertical)
        
        self.addToGroup(self.text)
        self.addToGroup(self.border)

    def paint(self, painter: QPainter or None, option: QStyleOptionGraphicsItem or None, widget: QWidget or None) -> None:
        border = self.border.boundingRect()
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setBrush(QtGui.QColor(Theme.shadow))
        painter.drawRoundedRect(
            int(Style.shadowXOffset),
            int(Style.shadowYOffset),
            border.width(),
            border.height(),
            int(Style.border_radius),
            int(Style.border_radius)
        )

        painter.setBrush(QtGui.QColor(Theme.secondaryColor))
        painter.setPen(QtGui.QPen(
            QtGui.QColor(Theme.shadow),
            int(Style.border_width.replace('px',''))
        ))
        painter.drawRoundedRect(
            border,
            int(Style.border_radius),
            int(Style.border_radius)
        )
        return super().paint(painter, option, widget)

    def setMargins(self, left, top, right, bottom):
        self.margin.left = left
        self.margin.right = right
        self.margin.top = top
        self.margin.bottom = bottom
        self.margin.horizontal = right + left
        self.margin.vertical = top + bottom

class HistoryBlock(QtWidgets.QGraphicsItemGroup):
    _date = str()
    _spacing = int(24)
    _width = float()

    @property
    def width(self):
        return self._width
    @width.setter
    def width(self,_w):
        self._width = _w

        for row in self.rows:
            row.resize(_w - self.margin.horizontal)

    @property
    def spacing(self):
        return self._spacing
    @spacing.setter
    def spacing(self, _s):
        self._spacing = _s

    @property
    def date(self):
        return self._date
    
    @date.setter
    def date(self, d):
        self._date = d

    class margin:
        left = 24
        right = 8
        top = 8
        bottom = 8
        horizontal = right + left
        vertical = top + bottom

    def __init__(self, date = '', data = [],  parent: QGraphicsItem or None = None):
        super().__init__()
        self.setFiltersChildEvents(True)

        self.date = date
        self.rows = list()
        
        self.title = QtWidgets.QGraphicsTextItem(date)
        self.title.setFont(QtGui.QFont(
            QtWidgets.QApplication.font().family(),
            int(Metrics.h1.replace('px','')),
            QtGui.QFont.Weight.Black
        ))
        self.title.setDefaultTextColor(QtGui.QColor('#515151'))
        
        self.addToGroup(self.title)
        self.line = QtWidgets.QGraphicsPathItem()
        self.line.setPen(QtGui.QPen(
            QtGui.QColor(Theme.shadow),
            int(Style.border_width.replace('px',''))
            ))
        path = QtGui.QPainterPath()
        
        path.moveTo(0,self.title.boundingRect().bottom() + self.margin.top)
        path.lineTo(QtCore.QPointF(0,self.childrenBoundingRect().bottom()))
        
        
        self.line.setPath(path)
        self.addToGroup(self.line)
        
       


        for kwargs in data:
            self.add(kwargs)
    
    
  

    def sceneEventFilter(self, watched: QGraphicsItem or None, event: QEvent or None) -> bool:
        if isinstance(watched, HistoryRow):
            if event.type() == QEvent.Type.GraphicsSceneHoverEnter:
                pass

            elif event.type() == QEvent.Type.GraphicsSceneHoverLeave:  
                pass

        return super().sceneEventFilter(watched, event)
    
   
    

    def add(self, kwargs:dict)->float:
        l = len(self.rows)
        index = 0

        row = HistoryRow(**kwargs)
        row.setParentItem(self)
        row.setAcceptHoverEvents(True)
        
        row.resize(self.width - self.margin.horizontal)
        row.setX(self.margin.left)

        if l:
            for i in range(l):
                if not Date.compare_time(self.rows[i].time, kwargs['time']):
                    break
                index += 1

            if index == l:
                row.setY(self.rows[-1].y() + self.rows[-1].height + self.spacing)
            else:
                row.setY(self.rows[index].y())

                for j in range(index, l):
                    self.rows[j].moveBy(
                        0, 
                        row.height + self.spacing)
        else:
            row.moveBy(
                0,
                self.title.boundingRect().height() + self.margin.top)

        self.rows.insert(index, row)
        self.addToGroup(row)


       
        path = self.line.path()
        path.setElementPositionAt(path.elementCount() - 1, 0,self.childrenBoundingRect().bottom())
        
        self.line.setPath(path)
        
        return row.height + self.spacing

    def setWidth(self, width:float) -> None:
        self.width = width



class HistoryScreenView(QtWidgets.QGraphicsView):
    _spacing = int(11)
    
    @property
    def spacing(self):
        return self._spacing
    @spacing.setter
    def spacing(self, _s):
        self._spacing = _s

    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()
    
    def __init__(self, model:object = None, controller:object = None):
        super().__init__()
        
        self.model = model
        self.controller = controller
        self.model.add_observer(self)

        self.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        self.scene = QtWidgets.QGraphicsScene()
        self.setViewportMargins(16,0,16,0)
        self.setContentsMargins(0,0,0,0)
        self.verticalScrollBar().setStyleSheet('QScrollBar{width:0px}')
        self.horizontalScrollBar().setDisabled(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setStyleSheet('background:transparent')
        self.blocks = []
        self.setScene(self.scene)

        self.image = QtWidgets.QGraphicsPixmapItem()
        self.image.setPixmap(QtGui.QPixmap(Path.image('history_screen_splash.png')))

        self.scene.addItem(self.image)


    
    def model_is_changed(self, t:Observer.ObserverEvent, data:dict):
        if t.type() == Observer.ObserverEvent.ADD:
            self.add(data['date'], data['data'])

    def add(self, date:str, kwargs:dict):
        l = len(self.blocks)
        if l:
            for i in range(l):
                if self.blocks[i].date == date:
                    dy = self.blocks[i].add(kwargs)
                    
                    for j in range(i + 1, l):
                        self.blocks[j].moveBy(0, dy)
    
                    return
                
            block = HistoryBlock(date,[kwargs])
            block.setWidth(self.viewport().width())
            self.scene.addItem(block)
            h = 0
            for i in range(l):
                if Date.compare(date, self.blocks[i].date):   
                    dy = block.childrenBoundingRect().height() + self.spacing
                
                    for j in range(i, l):
                        self.blocks[j].moveBy(0, dy)
                    
                    
                    self.blocks.insert(i, block)
                    block.setY(h)

                    return
                h += self.blocks[i].childrenBoundingRect().height() + self.spacing
            
            block.setY(h)            
            self.blocks.append(block)
            
        else:
            block = HistoryBlock(date,[kwargs])
            block.setWidth(self.viewport().width())
            self.scene.addItem(block)
            self.blocks.append(block)

        self.image.hide()

  
    def mousePressEvent(self, event: QMouseEvent or None) -> None:
       
        for item in self.items(event.pos()):
            if isinstance(item.parentItem(), HistoryRow):
                self.controller.onApply(item.parentItem().get())
           
                
        return super().mousePressEvent(event)
    
    def resizeEvent(self, event: QResizeEvent or None) -> None:
        sz = max(event.size().width(), event.size().height())
        self.image.setPixmap(
            self.image.pixmap().scaled(
                sz,sz,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )
        self.image.setPos(self.rect().center().toPointF() - self.image.boundingRect().center())


        for block in self.blocks:
            block.setWidth(event.size().width())
            
            
        return super().resizeEvent(event)
    