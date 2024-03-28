from PyQt6.QtCore import (
    QPoint,
    QVariantAnimation,
    QPropertyAnimation,
    Qt,
    QEasingCurve,
    QObject,
    QEvent
)
from PyQt6.QtGui import (
    QColor,
    QResizeEvent,
    QEnterEvent,

)
from PyQt6.QtWidgets import (
    QWidget,
    QTextEdit,
    QLabel,
)

from Utility.style import Theme, Icons, Style

class Comment(QWidget):
    hasMouse = False

    def __init__(self, comment = '', parent:QWidget = None) -> None:
        super().__init__(parent)

        self.setContentsMargins(6,8,6,8)
        
        self.shadow_style = {
            'border-style':'dashed',
            'border-radius':Style.border_radius,
            'border-width':'4px',
            'border-color':'black',
            'background-color':'transparent'
        }

        self.shadow = QWidget(self)
        self.shadow.move(QPoint(self.contentsMargins().left(), self.contentsMargins().top()))
        self.shadow.setStyleSheet(self.getStyle())

        self.textEdit = QTextEdit(self)
        
        self.textEdit.setObjectName('comment')
        self.textEdit.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.textEdit.installEventFilter(self)
        self.textEdit.move(QPoint(self.contentsMargins().left(), self.contentsMargins().top()))
        self.textEdit.verticalScrollBar().setStyleSheet('width:0px;')
        
        if comment:
            self.textEdit.blockSignals(True)
            self.textEdit.setText(comment)
            self.textEdit.blockSignals(False)
            
        self.icon = QLabel(self.textEdit)
        self.icon.setPixmap(Icons().plus)
        self.icon.setStyleSheet('border:none;background:transparent')
        
        
        self._anim_rect = QVariantAnimation(
            startValue = QPoint(self.contentsMargins().left(), self.contentsMargins().top()),
            endValue = QPoint(0,0),
            duration = 150,
            valueChanged = lambda point: self.textEdit.move(point),
            easingCurve = QEasingCurve.Type.InOutBack
        )
        
        self._anim_color = QVariantAnimation(
            startValue = QColor(217,217,217,.31*255),
            endValue = QColor(Theme.secondaryColor),
            valueChanged = lambda color: self.textEdit.setStyleSheet(f'background-color:rgba{color.getRgb()[:3] + (color.alphaF(),)}'),
            duration = 150,
            easingCurve = QEasingCurve.Type.InOutBack
        )
    
    def __del__(self):
        self._anim_color.stop()
        self._anim_rect.stop()
        self._anim_color.deleteLater()
        self._anim_rect.deleteLater()
        
    def getStyle(self):
        return ';'.join([f'{key}:{value}' for key,value in self.shadow_style.items()])
    
    def eventFilter(self, obj: QObject or None, event: QEvent or None) -> bool:
        if obj == self.textEdit:
            
            if event.type() == QEvent.Type.FocusOut and not self.hasMouse:
                self.setElevation(False)
                self.shadow_style['border-style'] = 'dashed'
                self.shadow_style['background-color'] = 'transparent'

                self.shadow.setStyleSheet(self.getStyle())
                self.textEdit.blockSignals(True)
                self.textEdit.setText(self.textEdit.toPlainText().strip())
                self.textEdit.blockSignals(False)
                
                if not len(self.textEdit.toPlainText()):
                    self.icon.show()

            elif event.type() == QEvent.Type.FocusIn:
                self.shadow_style['border-style'] = 'solid'
                self.shadow_style['background-color'] = Theme.shadow
                
                self.shadow.setStyleSheet(self.getStyle())

                self.icon.hide()
        return super().eventFilter(obj, event)


    def resizeEvent(self, a0: QResizeEvent or None) -> None:
        size = a0.size()
        
        size.setWidth(size.width() - self.contentsMargins().left() - self.contentsMargins().right())
        size.setHeight(size.height() - self.contentsMargins().top() - self.contentsMargins().bottom())

        self.shadow.resize(size)
        self.textEdit.resize(size)

        center = self.textEdit.size()/2 - self.icon.pixmap().size()/2
        self.icon.move(center.width(), center.height())
        
        return super().resizeEvent(a0)
    
    
    def enterEvent(self, event: QEnterEvent or None) -> None:
        self.hasMouse = True

        if not self.textEdit.hasFocus():
            self.setElevation(True)

        return super().enterEvent(event)
    def leaveEvent(self, a0: QEvent or None) -> None:
        self.hasMouse = False

        if not self.textEdit.hasFocus():
            self.setElevation(False)

        return super().leaveEvent(a0)
    def setElevation(self, elevate = True):
        direction = QPropertyAnimation.Direction.Forward if elevate else QPropertyAnimation.Direction.Backward

        self._anim_rect.setDirection(direction)
        self._anim_color.setDirection(direction)

        self._anim_rect.start()
        self._anim_color.start()
 