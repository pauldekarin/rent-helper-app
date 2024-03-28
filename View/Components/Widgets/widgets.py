from PyQt6.QtWidgets import (
    QWidget,
    QSizePolicy,
    QStackedLayout,
    QVBoxLayout,
    QPushButton,
    QLineEdit
)

from PyQt6.QtCore import (
    QVariantAnimation,
    QEasingCurve,
    QEvent,
    QObject
)

from PyQt6.QtGui import (
    QEnterEvent,
    QPaintEvent,
    QPainter,
)
from Utility.style import Style, Theme, Icons, Metrics


class Widget(QWidget):
    _instance = None

    def __init__(self, objClass = None, parent: QWidget or None = None, **kwargs) -> None:
        super().__init__(parent)
        
        self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Ignored))
        self.setContentsMargins(0,0,0,0)
     
        self.setStyleSheet(
            '''
                #instance{{
                    border:{borderWidth} solid {borderColor};
                    border-radius:{borderRadius};                    
                }}
                #shadow{{
                    border:{borderWidth} solid {borderColor};
                    border-radius:{borderRadius};
                    background:transparent;
                }}
            '''.format(
                    borderWidth = int(Style.border_width.replace('px','')),
                    borderRadius = int(Style.border_radius),
                    borderColor = Theme.shadow,
                    windowColor = Theme.window,
                    objClass = objClass.__name__
            )
        )
        
        mLayout = QStackedLayout(self)
        mLayout.setStackingMode(QStackedLayout.StackingMode.StackAll)

        container = QWidget()
        self._instanceLayout = QVBoxLayout(container)
        self._instanceLayout.setContentsMargins(0,0,Style.shadowXOffset,Style.shadowYOffset)

        self._instance = objClass(**kwargs)
        self._instance.setObjectName('instance')
    
        self._instance.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Ignored))
        
        self._instanceLayout.addWidget(self._instance)
        
        mLayout.addWidget(container)
        

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(
            Style.shadowXOffset,
            Style.shadowYOffset,
            0,0
        )

        self._shadow = QWidget()
        self._shadow.setObjectName('shadow')

        layout.addWidget(self._shadow)

        mLayout.addWidget(container)

  

    def __str__(self) -> str:
        return 'Widget'
    def setShadowColor(self, color:str):
        self._shadow.setStyleSheet(f'background:{color}')
    
    def setShadowFill(self, fill = True):
        self._shadow.setStyleSheet('background:{}'.format(Theme.shadow if fill else 'transparent'))

    def shadow(self):
        return self._shadow
    
    def instance(self):
        return self._instance
    
    # def setSizePolicy(self, sizePolicy:QSizePolicy):
    #     if self._instance:
    #         self._instance.setSizePolicy(sizePolicy)
    #     return super().setSizePolicy(sizePolicy)

        

class Button(Widget):
    def __init__(self, parent: QWidget = None, **kwargs) -> None:
        super().__init__(QPushButton, parent, **kwargs)

        self._anim = QVariantAnimation(
            startValue = 0,
            endValue = 100,
            valueChanged = self.hoverAnimHandler,
            duration = 150,
            easingCurve = QEasingCurve.Type.InOutBack
        )

    def __str__(self) -> str:
        return 'Button'
    def hoverAnimHandler(self, t):
        self.instance().move(
            Style.shadowXOffset*t/100,
            Style.shadowYOffset*t/100
        )

    def enterEvent(self, event: QEnterEvent or None) -> None:
        self._anim.setDirection(QVariantAnimation.Direction.Forward)
        self._anim.start()

        return super().enterEvent(event)
    def leaveEvent(self, a0: QEvent or None) -> None:
        self._anim.setDirection(QVariantAnimation.Direction.Backward)
        self._anim.start()
        return super().leaveEvent(a0)


class LineEdit(Widget):
    def __init__(self, parent: QWidget = None, **kwargs) -> None:
        super().__init__(QLineEdit, parent, **kwargs)

        self._anim = QVariantAnimation(
            startValue = 0,
            endValue = 100,
            valueChanged = self.onAnimHandler,
            duration = 150,
            easingCurve = QEasingCurve.Type.InOutCirc
        )

        self.instance().installEventFilter(self)
    def __str__(self) -> str:
        return 'LineEdit'
 
    def eventFilter(self, a0: QObject or None, a1: QEvent or None) -> bool:
        if a0 == self.instance():
            if a1.type() == QEvent.Type.FocusIn:
                self._anim.setDirection(QVariantAnimation.Direction.Forward)
                self._anim.start()
            elif a1.type() == QEvent.Type.FocusOut:
                self._anim.setDirection(QVariantAnimation.Direction.Backward)
                self._anim.start()

        return super().eventFilter(a0, a1)
    def onAnimHandler(self, t):
        t1 = min(t/100,.999)
        t2 = min(t1 + 0.0001,1)

        sheet = '''
            background:qlineargradient(
                x1:0 y1:0, x2:1 y2:0, 
                stop:0 {color}, 
                stop:'''+str(t1)+''' {color}, 
                stop:'''+str(t2)+''' {background},
                stop:1 {background})'''
        
        self.instance().setStyleSheet(sheet.format(
            color = Theme.secondaryColor,
            background = Theme.window

        ))
        self.shadow().setStyleSheet(sheet.format(
            color = Theme.shadow,
            background = 'transparent'
        ))
