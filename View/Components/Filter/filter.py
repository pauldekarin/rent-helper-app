import typing
import json
import re
from PyQt6 import QtCore, QtGui, QtWidgets

from PyQt6.QtGui import (
    QColor
)
from PyQt6.QtCore import (
    QPointF,
    QVariantAnimation,
    QVariant,
    QEasingCurve,
    QObject,
    QEvent,
    Qt,
    QRectF,
    pyqtSignal,
    pyqtSlot,
    QStringListModel,
)
from PyQt6.QtWidgets import (
    QGridLayout,
    QStackedLayout,
    QCompleter,
    QSizePolicy,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit
)

from Utility.style import Style,Theme,Icons, Metrics
from Utility.path import Path

class CheckItem(QWidget):
    def __init__(self, parent: QWidget or None = None, text:str = '') -> None:
        super().__init__(parent)

        self.setStyleSheet(
            '''
                #button{{
                    border-width:4px;
                    border-style:solid;
                    border-radius:{borderRadius};
                    border-color:#000000;
                    background:{background};
                    font-size:{fontSize};
                    font-weight:900;
                    color:{color};
                }}
            '''.format(
                    background = 'transparent',
                    fontSize = Metrics.p,
                    color=Theme.secondaryTextColor,
                    borderRadius = Style.border_radius)
        )

        layout = QStackedLayout(self)
        layout.setStackingMode(QStackedLayout.StackingMode.StackAll)

        self.ripple_t = 0
        self.ripple_pos = QPointF()
        
        
        self.shadow = QWidget()
        self.shadow.move(self.contentsMargins().right(), self.contentsMargins().bottom())
        self.shadow.setStyleSheet(
            '''
                border-width:4px;
                border-style:solid;
                border-radius:{border_radius};
                border-color:#000000
            '''.format(border_radius = Style.border_radius)
        )
        self.ripple = QWidget()
        self.ripple.setStyleSheet(
            '''
                background:{background};
                border-radius:{border_radius};
            '''.format(
                    background = Theme.primaryColor,
                    border_radius = Style.border_radius)
        )
        self.ripple.installEventFilter(self)

        self.button = QPushButton(text = text)
        self.button.setStyleSheet(
            '''
                border-width:4px;
                border-style:solid;
                border-radius:{borderRadius};
                border-color:#000000;
                background:{background};
                font-size:{fontSize};
                font-weight:900;
                color:{color};
                padding:8px;
            '''.format(
                    background = 'transparent',
                    fontSize = Metrics.p,
                    color=Theme.secondaryTextColor,
                    borderRadius = Style.border_radius)
        )
        self.button.setContentsMargins(0,0,6,8)
        self.button.installEventFilter(self)
        self.button.setCheckable(True)
        self.button.pressed.connect(self.pressed)
        
        layout.addWidget(self.button)
        layout.addWidget(self.ripple)
        layout.addWidget(self.shadow)

        self._anim_ripple = QVariantAnimation(
            startValue = QVariant(0),
            endValue = QVariant(50),
            valueChanged =  self.onAnimRipple,
            duration = 200,
            easingCurve = QEasingCurve.Type.InOutSine
        )
    def pressed(self):
        if not self.button.isChecked():
            self._anim_ripple.setStartValue(self._anim_ripple.currentValue())
            self._anim_ripple.setEndValue(QVariant(100))

            self._anim_ripple.start()
        else:
            
            self.ripple_pos = self.button.mapFromGlobal(QtGui.QCursor.pos())

            self._anim_ripple.setStartValue(self._anim_ripple.currentValue())
            self._anim_ripple.setEndValue(QVariant(50))
            self._anim_ripple.start()
            

    def onAnimRipple(self, t):
        self.ripple_t = t/100
        self.ripple.update()

    def eventFilter(self, obj: QObject or None, event: QEvent or None) -> bool:
        if obj == self.ripple:
            if event.type() == QEvent.Type.Paint:
                painter = QtGui.QPainter()
                painter.begin(obj)
                clipPath = QtGui.QPainterPath()
                clipPath.addRoundedRect(QRectF(self.button.geometry()), 20,20)
                r = max(obj.height(),obj.width())*self.ripple_t
                painter.setClipPath(clipPath)
                painter.setBrush(QtGui.QBrush(QColor(Theme.secondaryColor)))
                painter.setPen(Qt.PenStyle.NoPen)
                
                painter.drawEllipse(self.ripple_pos, r,r)
                painter.end()
                return True

        elif obj == self.button and not self.button.isChecked():
            if event.type() == QEvent.Type.Enter:
                self._anim_ripple.setStartValue(QVariant(0))
                self._anim_ripple.setEndValue(QVariant(50))
                self._anim_ripple.setDirection(QVariantAnimation.Direction.Forward)
                self.ripple_pos = self.button.mapFromGlobal(QtGui.QCursor.pos())
                self._anim_ripple.start()

            elif event.type() == QEvent.Type.Leave:
                self._anim_ripple.setStartValue(QVariant(0))
                self._anim_ripple.setEndValue(QVariant(50))
                self._anim_ripple.setDirection(QVariantAnimation.Direction.Backward)
                self.ripple_pos = self.button.mapFromGlobal(QtGui.QCursor.pos())
                self._anim_ripple.start()
                
              
            
        return super().eventFilter(obj, event)

    def setChecked(self, checked):
        self.button.setChecked(checked)

        if self.underMouse():
            self._anim_ripple.setStartValue(self._anim_ripple.currentValue())
            
        else:
            self.ripple_pos = self.rect().center()
            self._anim_ripple.setStartValue(QVariant(0))
        
        self._anim_ripple.setEndValue(QVariant(100 if checked else 0))
        self._anim_ripple.start()


    def resizeEvent(self, event: QtGui.QResizeEvent or None) -> None:
        size = self.button.geometry()
        size.setSize(QtCore.QSize(size.width() - 6, size.height() - 8))

        self.button.setGeometry(size)
        self.ripple.setGeometry(size)

        size.moveTopLeft(QtCore.QPoint(6,8))
        
        self.shadow.setGeometry(size)
        return super().resizeEvent(event)
class CheckList(QWidget):
    def __init__(self, parent: QWidget or None = None) -> None:
        super().__init__(parent)
        layout = QGridLayout()

  
        item = CheckItem(text='1')
        item.setStyleSheet('border:none; background:none')

        layout.addWidget(item,0,0)

        item = CheckItem(text='2')
        item.setStyleSheet('border:none; background:none')
        layout.addWidget(item,0,1)

        item = CheckItem(text='3')
        item.setStyleSheet('border:none; background:none')
        layout.addWidget(item,0,2)

        item = CheckItem(text='4')
        item.setStyleSheet('border:none; background:none')
        layout.addWidget(item,0,3)

        item = CheckItem(text='5+')
        item.setStyleSheet('border:none; background:none')
        layout.addWidget(item,1,0)

        item = CheckItem(text='Свободная')
        item.setStyleSheet('border:none; background:none')
        layout.addWidget(item,1,1, 1,3)

        item = CheckItem(text='Студия')
        item.setStyleSheet('border:none; background:none')
        layout.addWidget(item,2,0,1,2)
        self.setLayout(layout)
    
    def set(self, _rm):
        for i in range(self.layout().count()):
            _inst = self.layout().itemAt(i).widget()
            _inst.setChecked(_inst.button.text() in _rm)

    def clear(self):
        
        for i in range(self.layout().count()):
            self.layout().itemAt(i).widget().setChecked(False)

    def get(self):        
        return [self.layout().itemAt(i).widget().button.text() 
                    for i in range(self.layout().count()) if self.layout().itemAt(i).widget().button.isChecked()]

class LineEdit(QLineEdit):
    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()
    def keyPressEvent(self, a0: QtGui.QKeyEvent or None) -> None:
        super().keyPressEvent(a0)

        if a0.key() != 16777220:
            self.completer().complete(QtCore.QRect(
                        0,
                        8,
                        self.width(),
                        self.completer().widget().height()
                    ))
class DropDown(QWidget):
    focused = pyqtSignal(bool)

    def __init__(self, parent: QWidget or None = None) -> None:
        super().__init__(parent)

        layout = QStackedLayout(self)
        layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        self.setStyleSheet(
            '''
                #border{{
                    border:4px solid black;
                    border-radius:10px;
                }}
                QLineEdit{{
                    padding:16px;
                    background:transparent;
                    color:{textColor};
                    font-weight:900;
                    font-size:{fontSize}
                }}
                QLineEdit[text=\"\"]{{
                    color:{placeholder}
                }}
            '''.format(
                    placeholder = Theme.secondaryTextColor,
                    textColor = Theme.secondaryColor,
                    fontSize = Metrics.h2
            )
        )

        with open(Path.json('cities.json')) as f_in:
            js_in = json.load(f_in)

            self.words = js_in.keys()

        self.completer = QCompleter(self.words, self)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)        
        self.completer.popup().setSpacing(4)
        self.completer.popup().verticalScrollBar().setStyleSheet('QScrollBar{width:0px}')
        self.completer.popup().setStyleSheet(
            '''
                QAbstractItemView{{
                    background:{background};
                    border:{borderWidth} solid {borderColor};
                    font-weight:900;
                }}
                QAbstractItemView::item{{
                    background:{background};
                    border:{borderWidth} solid {borderColor};
                }}
                QAbstractItemView::item:hover{{
                    color:{hoverColor}
                }}
            '''.format(
                    background = Theme.primaryColor,
                    borderWidth = Style.border_width,
                    borderColor = Theme.shadow,
                    borderRadius = Style.border_radius,
                    hoverColor = Theme.secondaryColor
            )
        )
        
        self.lineEdit = LineEdit()
        self.lineEdit.setObjectName('border')
        self.lineEdit.setContentsMargins(
            0,0,
            int(Style.shadowXOffset),
            int(Style.shadowYOffset)
        )
        self.lineEdit.setPlaceholderText('Город')
        self.lineEdit.returnPressed.connect(lambda *args :self.lineEdit.clearFocus())
        self.lineEdit.setStyleSheet(
            '''
                background:{background}
            '''.format(background = Theme.primaryColor)
        )
        self.lineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineEdit.textChanged.connect(lambda *args: self.style().polish(self.lineEdit))
        self.lineEdit.editingFinished.connect(self.editingFinished)
        self.lineEdit.setCompleter(self.completer)
        self.lineEdit.installEventFilter(self)
        self.lineEdit.setText(self.completer.currentCompletion())
        
        self.completer.popup().installEventFilter(self)
        self.completer.activated.connect(self.lineEdit.clearFocus)

        self.shadow = QLineEdit()
        self.shadow.setReadOnly(True)
        self.shadow.setObjectName('border')
        self.shadow.setContentsMargins(
            int(Style.shadowXOffset),
            int(Style.shadowYOffset),
            0,0
        )

        layout.addWidget(self.lineEdit)
        layout.addWidget(self.shadow)

        self.scaleAnimation = QVariantAnimation(
            startValue = 100,
            endValue = 0,
            valueChanged = lambda t:self.lineEdit.setContentsMargins(0,0, Style.shadowXOffset*t/100, Style.shadowYOffset*t/100),
            duration = 150,
            easingCurve = QEasingCurve.Type.InOutQuad
        )

    def editingFinished(self):
        if not self.lineEdit.hasFocus():
            if self.lineEdit.text() not in self.words:
                self.lineEdit.clear()

    def eventFilter(self, obj: QObject or None, event: QEvent or None) -> bool:
        if obj == self.lineEdit:
            if event.type() == QEvent.Type.MouseButtonPress and self.lineEdit.hasFocus():
                self.scaleAnimation.setDirection(QVariantAnimation.Direction.Forward)
                self.scaleAnimation.start()
                
                self.focused.emit(True)

            elif event.type() == QEvent.Type.FocusOut and not self.lineEdit.hasFocus():
                self.scaleAnimation.setDirection(QVariantAnimation.Direction.Backward)
                self.scaleAnimation.start()

                self.focused.emit(False)

        return super().eventFilter(obj, event)
    
class Input(QWidget):
    def __init__(self, parent:QWidget or None = None)->None:
        super(Input,self).__init__(parent=parent)
        
        layout = QStackedLayout()
        layout.setStackingMode(QStackedLayout.StackingMode.StackAll)

        self.shadow = QLineEdit()
        self.shadow.setStyleSheet(
            '''
                border:4px solid black;
                border-radius:{border_radius};
                background:transparent;
                padding:4px;
            '''.format(border_radius=Style.border_radius)
        )
        self.shadow.setContentsMargins(6,8,0,0)        
        self.shadow.setReadOnly(True)

        self.lineEdit = QLineEdit()
        self.lineEdit.setStyleSheet(
            '''
                QLineEdit{{
                    border:4px solid black;
                    border-radius:{border_radius};
                    background:{background};
                    padding:16px;
                    font-weight:900;
                    font-size:{h2};
                    color:{color};
                }}
                QLineEdit[text=\"\"]{{
                    color:{focus};
                }}
            '''.format(
                    background = Theme.primaryColor,
                    border_radius = Style.border_radius,
                    h2 = Metrics.h2,
                    color = Theme.secondaryColor,
                    focus = Theme.secondaryTextColor
            )
        )
        self.lineEdit.setContentsMargins(0,0,6,8)
        self.lineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineEdit.textEdited.connect(self.textEdited)

        layout.addWidget(self.shadow)
        layout.addWidget(self.lineEdit)

        self.setLayout(layout)

    def textEdited(self, text:str):
        self.style().polish(self.lineEdit)
        if text == '0':
            self.lineEdit.clear()

            return        
        
        try:
            self.lineEdit.setText('{:,}'.format(int(re.sub(r"[^\d]","", text))).replace(',', '  '))
        except ValueError:
            self.lineEdit.clear()


    def setPlaceholderText(self, placeHolder):
        self.lineEdit.setPlaceholderText(placeHolder)

class Filter(QWidget):
    submit = pyqtSignal(str, list, list)

    def __init__(self, parent:QWidget or None = None) -> None:
        super(Filter, self).__init__(parent=parent)
        layout = QVBoxLayout(self)

        ##Styling
        self.setStyleSheet(
            '''
                #title{{
                    color:{color};
                    background:transparent;
                    border:none;
                    font-size:{h1};
                    font-weight:900
                }}
                #button{{
                    background:transparent;
                    border:none;
                }}
            '''.format(color = Theme.primaryTextColor, h1 = Metrics.h1)
        )


        ##City Filter

        #layout
        l = QVBoxLayout()

        self.dropDown = DropDown()
        
        self.dropDown.focused.connect(self.dropdownFocused) #Hide other filters on focus

        l.addWidget(QLabel('Город',objectName = 'title'), alignment=Qt.AlignmentFlag.AlignCenter)  #Title
        l.addWidget(self.dropDown,stretch=1) #Input Edit with DropDown of cities
        
        layout.addLayout(l, stretch=1)


        ##Price filter

        #set content to frame for opportunity to hide it
        self.priceFrame = QtWidgets.QFrame() 
        sp_retain = self.priceFrame.sizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.priceFrame.setSizePolicy(sp_retain)

        #layout
        l = QVBoxLayout()
        l.setContentsMargins(0,0,0,0)


        #title
        l.addWidget(QLabel(text ='Цена' ,objectName = 'title'), alignment= Qt.AlignmentFlag.AlignCenter)
        self.inputs = []

        #inputs
        for t in ['От', 'До']:
            input = Input()
            input.setPlaceholderText(t)
            # input.lineEdit.setValidator(QtGui.QIntValidator())
            l.addWidget(input)
            
            self.inputs.append(input)

        self.priceFrame.setLayout(l)

        layout.addWidget(self.priceFrame, stretch=1)
        

        ##Rooms filter

        #set content to frame for opportunity to hide it
        self.checkFrame = QtWidgets.QFrame()

        sp_retain = self.checkFrame.sizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.checkFrame.setSizePolicy(sp_retain)

        #layout
        l = QVBoxLayout()
        l.setContentsMargins(0,0,0,0)

        self.checkList = CheckList()
        
        #title
        l.addWidget(QLabel(text='Комнаты',objectName='title'), alignment=Qt.AlignmentFlag.AlignCenter)
        l.addWidget(self.checkList, stretch=1)
        
        self.checkFrame.setLayout(l)

        layout.addWidget(self.checkFrame, stretch=2)


        ##Control buttons

        #layout
        l = QHBoxLayout()
        l.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMinAndMaxSize)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.setSpacing(4)
        l.setContentsMargins(0,0,0,0)

        #apply button
        apply = QPushButton(objectName = 'button')
        apply.setIcon(QtGui.QIcon(Icons(color = None, size = QtCore.QSize(48,48)).checkmark))
        apply.setIconSize(QtCore.QSize(48,48))
        apply.clicked.connect(self.apply)

        l.addWidget(apply)

        #refresh button (clear filter)
        refresh = QPushButton(objectName = 'button')
        refresh.setIcon(QtGui.QIcon(Icons(color = None, size = QtCore.QSize(48,48)).refresh))
        refresh.setIconSize(QtCore.QSize(48,48))
        refresh.released.connect(self.clear)

        l.addWidget(refresh)

        layout.addLayout(l, stretch=1)
    
    @pyqtSlot()
    def apply(self):
        if self.dropDown.completer.currentCompletion() != '':
            self.submit.emit(
                self.dropDown.completer.currentCompletion(),
                [
                    self.inputs[0].lineEdit.text().replace(' ',''), 
                    self.inputs[1].lineEdit.text().replace(' ','')
                 ] ,
                self.checkList.get()
            )

    def set(self, city:str, price:list, rooms:list):
        self.dropDown.lineEdit.setText(city)
        self.inputs[0].lineEdit.setText(price[0])
        self.inputs[1].lineEdit.setText(price[1])
        self.checkList.set(rooms)

    @pyqtSlot()
    def clear(self):
        self.dropDown.lineEdit.setText('')
        
        for item in self.inputs:
            item.lineEdit.setText('')
            item.lineEdit.textEdited.emit('')

        self.checkList.clear()
        
    @pyqtSlot(bool)
    def dropdownFocused(self, focused):
        
        if focused:
            self.priceFrame.hide()
            self.checkFrame.hide()

        else:
            self.priceFrame.show()
            self.checkFrame.show()
                