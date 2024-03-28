import sys
import os
import math
import logging

from pathlib import Path

from PyQt6 import QtCore, QtGui, QtWidgets

from PyQt6.QtGui import (
    QCloseEvent,
    QFontDatabase, 
    QMouseEvent,
    QPixmap, 
    QIcon,
    QColor
)

from PyQt6.QtCore import  (
    QEvent,
    Qt, 
    QSize,
    pyqtSignal,
    pyqtSlot,
    QVariantAnimation,

)
from PyQt6.QtWidgets import (
    QApplication, 
    QHBoxLayout,
    QVBoxLayout,
    QLabel, 
    QMainWindow, 
    QLineEdit,
    QWidget,
    QTextEdit,
    QPushButton,
    QStackedWidget,
 )

from View.screens import screens
from Controller.main_screen import MainController

from Utility.style import Style, Theme, Metrics, Icons
from Utility.path import Path

class SidebarItem(QPushButton):
    _checked = False
    _clipPath = QtGui.QPolygonF()
    _fov = 60
    _mousePos = None
    _angle = 0

    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()
    
    def __str__(self) -> str:
        return 'SidebarItem'
    
   
    def setClipPath(self, pos):
        len = 2000
        coordinates = pos - self.rect().center()
        
        self.angle = math.atan2(coordinates.y(),coordinates.x() if coordinates.x() != 0 else .00001)/math.pi*180
        a1 = math.radians(self.angle + self.fov/2)
        a2 = math.radians(self.angle - self.fov/2)

        self.clipPath = QtGui.QPolygonF([
            (QtCore.QPoint(
                int(math.cos(a2)*len),
                int(math.sin(a2)*len)
            ) + self.rect().center()).toPointF() , 
            pos.toPointF(), 
            (QtCore.QPoint(
                int(math.cos(a1)*len),
                int(math.sin(a1)*len)
            ) + self.rect().center()).toPointF()
            ])
        
    def mouseMoveEvent(self, event: QMouseEvent or None) -> None:
        if not self.checked:
            self.mousePos = event.pos()
            self.setClipPath(event.pos())
            self.update()

        return super().mouseMoveEvent(event)

    @property
    def fov(self):
        return self._fov
    @fov.setter
    def fov(self, fov):
        self._fov = fov

    @property
    def clipPath(self):
        return self._clipPath
    @clipPath.setter
    def clipPath(self, polygon):
        self._clipPath = polygon

    @property
    def angle(self):
        return self._angle
    @angle.setter
    def angle(self, angle):
        self._angle = angle

    @property
    def mousePos(self):
        return self._mousePos
    @mousePos.setter
    def mousePos(self, pos):
        self._mousePos = pos

    @property
    def checked(self):
        return self._checked
    
    @checked.setter
    def checked(self, event: bool) -> None:
        self._checked = event

        if event:
            
            if not self.underMouse():
                self.setClipPath(self.rect().center())

            a = math.radians(self.angle + 180)

            self.anim = QVariantAnimation(
                startValue = QtCore.QPoint(0,0),
                endValue = QtCore.QPoint(
                    int(math.cos(a)*min(self.width(), self.height())),
                    int(math.sin(a)*min(self.width(), self.height()))
                ),
                valueChanged = lambda point: (
                    self.clipPath.translate(point.toPointF()),
                    self.update()
                )
            )
            self.anim.start()
        else:
            self.clipPath.clear()
            self.update()
        

   
    def leaveEvent(self, event: QEvent or None) -> None:
        self.mousePos = QtCore.QPoint(0,0)

        if not self.checked:
            self.clipPath.clear()
            self.update()

        return super().leaveEvent(event)
    
    def paintEvent(self, event: QtGui.QPaintEvent or None) -> None:
        super().paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(QColor(Theme.secondaryColor),4))
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        clipPath = QtGui.QPainterPath()
        clipPath.addPolygon(self.clipPath)
        
        painter.setClipPath(clipPath)
            
        painter.drawRoundedRect(self.rect().toRectF(), int(Style.border_radius),int(Style.border_radius))


class SideBar(QWidget):
    changed = pyqtSignal(str)

    def __init__(self, parent: QWidget or None = None) -> None:
        super().__init__(parent)
        
        self.setMouseTracking(True)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet(
            '''
                SideBar{{
                    background:{sidebar};
                    border-right:4px solid black;
                }}
                #button{{
                    text-align:left;
                    font-weight:900;
                    font-size:{p};
                    background:{background};
                    border:4px solid black;
                    border-radius:{border_radius};
                    padding:16px;
                    color:{primaryTextColor};
                }}
            '''.format(
                background = '#EDEDED',
                sidebar = Theme.sidebar,
                p = Metrics.p,
                border_radius = Style.border_radius,
                primaryTextColor=Theme.primaryTextColor
            )
        )
        self.current = None
        self.mousePos = None
        self.hoveredItem = None
        self.items = []

        layout = QVBoxLayout(self)
        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMaximumSize)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(40)
        
        button = SidebarItem(
            objectName = 'button'
        )

        button.setCheckable(False)
        button.checked = True
        button.setIcon(
            QtGui.QIcon(Icons().user)
        )
        button.setMouseTracking(True)
        
        button.clicked.connect(
            lambda checked, instance = button, nameScreen = 'user screen': self.clicked(instance,nameScreen))
        
        self.items.append(button)

        layout.addWidget(button,alignment=Qt.AlignmentFlag.AlignLeft)

        self.navLayout = QVBoxLayout()
        self.navLayout.setSpacing(16)
        
        layout.addLayout(self.navLayout)

    def mouseMoveEvent(self, event: QMouseEvent or None) -> None:
        if self.hoveredItem:
            self.mousePos = event.pos()
            self.hoveredItem.update()
        return super().mouseMoveEvent(event)
    

    def addScreen(self, nameScreen, icon:str or QIcon = None):
        button = SidebarItem(
            text = nameScreen,
            objectName = 'button'
        )
        button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        button.setCheckable(False)
        
        button.setIcon(
            icon if isinstance(icon, QIcon) else QIcon(Icons(size = QSize(48,48)).__load__(icon))
        )
        button.setMouseTracking(True)
        
        button.clicked.connect(
            lambda checked, instance = button, nameScreen = nameScreen: self.clicked(instance,nameScreen))
        
        self.items.append(button)

        self.navLayout.addWidget(button)

  
    def setItem(self, name:str):
        for index in range(self.navLayout.count()):
            item = self.navLayout.itemAt(index).widget() #SideBarItem
          

            if item.text() == name:
                item.checked = True
                self.current = item
               

            else:
                item.checked = False


    def clicked(self, instance:SidebarItem, nameScreen):
        if self.current != instance:
            for item in self.items:
                if item != instance:
                    item.checked = False
            instance.checked = True
            self.current = instance
            self.changed.emit(nameScreen)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Rent Helper(Beta)')

        self.controller = MainController()
        self.controller.view = self

        centralWidget = QWidget()
        
        layout = QHBoxLayout(centralWidget)

        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        #Initialize left SideBar
        self.sidebar = SideBar()
        self.sidebar.changed.connect(self.setCurrentScreen)
        layout.addWidget(self.sidebar)

        self.screenManager = QStackedWidget()
        
        
        layout.addWidget(self.screenManager, stretch=1)

        #Load background foreground styled image
        self.image = QLabel(centralWidget)
        self.image.setFixedSize(QSize(200,300))
        self.image.setScaledContents(True)
        self.image.setPixmap(QPixmap(Path.image('leaf.png')).scaled(
                self.image.width(), self.image.height(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        ))

        try:
            #Initialize APP settings
            self.loadFonts()
            self.resize(QSize(1000,600))
            self.setCentralWidget(centralWidget)
            self.loadScreens()

        except Exception as e:
            pass
        
        self.controller.onStart()

        

    def loadScreens(self):
        for screen in screens:
            model = screens[screen]['model']()
            controller = screens[screen]['controller'](model = model, m_controller = self.controller, name = screen)
            view = controller.get_view()

            if screen != 'user screen':
                view.setAccessibleName(screens[screen]['name'])
                self.sidebar.addScreen(screens[screen]['name'], Path.icon(screens[screen]['icon']))
            else:
                view.setAccessibleName(screen)

            self.screenManager.addWidget(view)

            

            self.controller.addController(screen, controller)
        
        self.setCurrentScreen('user screen')

    def loadFonts(self):
        QFontDatabase.addApplicationFont(os.path.join(os.getcwd(), 'assets/fonts/Piazzolla/Piazzolla.ttf'))

    def setScreen(self, nameScreen):
        self.sidebar.setItem(name=nameScreen)
        self.setCurrentScreen(nameScreen)
        

    @pyqtSlot(str)
    def setCurrentScreen(self, nameScreen):
    
        for sc_index in range(self.screenManager.count()):
            screen = self.screenManager.widget(sc_index)

            if screen.accessibleName() == nameScreen:
                self.screenManager.setCurrentWidget(screen)
                
                return
            


    def resizeEvent(self, event: QtGui.QResizeEvent or None) -> None:
        height = event.size().height()
        dy = height - self.image.height() + 10
        dx = -10

        self.image.move(dx,dy)
        return super().resizeEvent(event)
   
    
    def mousePressEvent(self, event: QMouseEvent or None) -> None:
        focused = QApplication.focusWidget()
        if isinstance(focused, QTextEdit) or isinstance(focused, QLineEdit):
            focused.clearFocus()

        return super().mousePressEvent(event)
    
    def closeEvent(self, a0: QCloseEvent or None) -> None:
        self.controller.onClose()

        return super().closeEvent(a0)
        

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("debug.log"),
            logging.StreamHandler()
        ]
    )
    Path.set_basedir("./")
    
    app = QApplication(sys.argv)
    app.setStyleSheet(Style.sheet)   

    

    QtGui.QFontDatabase.addApplicationFont(Path.font('Piazzolla/Piazzolla.ttf'))
    window = MainWindow()
    window.show()
    
    app.exec()
    