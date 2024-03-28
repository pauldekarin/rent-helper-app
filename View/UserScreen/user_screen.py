from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QEvent, QObject, Qt
from PyQt6.QtGui import QEnterEvent, QFocusEvent, QPaintEvent

from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QSizePolicy
)

from Utility.style import Style,Metrics,Icons,Theme
from Utility.observer import Observer
from Utility.path import Path

from View.Components.Widgets.widgets import LineEdit, Button, Widget

class UserScreenView(QWidget):

    class Type:
        AUTHENTICATION = 0
        REGISTRATION = 1
    
    _type = None

    @property
    def type(self):
        return self._type
    
    @type.setter
    def type(self, _t:Type):
        if self._type != _t:
            self._type = _t

            if _t == self.Type.REGISTRATION:
                self.toggleTitle.setText('А у меня уже есть аккаунт!')
                self.toggleButton.instance().setText('Войти')
                self.confirm.show()
            else:
                self.toggleTitle.setText('Хочу плюшечки!')
                self.toggleButton.instance().setText('Зарегистрироваться')
                self.confirm.hide()




    def __init__(self, parent: QWidget or None = None, model:object = None, controller:object = None) -> None:
        super().__init__(parent)
        self.model = model
        self.controller = controller
        self.model.add_observer(self)

        self.setStyleSheet(
            '''
                #title{{
                    font-size:{h1};
                    font-weight:900;
                    color:{secondaryTextColor}
                }}
                QLineEdit{{
                    font-size:{h2};
                    padding:10px;
                    font-weight:900;
                    background:{window}
                }}
                QPushButton{{
                    padding:16px;
                    font-size:{h2};
                    font-weight:900;
                    color:{secondaryTextColor};
                    background:{secondaryColor};
                }}
            
                #decor{{
                    background:{primaryColor}
                }}
            '''.format(
                    window = Theme.window,
                    h2 = Metrics.h2,
                    h1 = Metrics.h1,
                    secondaryTextColor = Theme.secondaryTextColor,
                    secondaryColor = Theme.secondaryColor,
                    primaryColor = Theme.primaryColor
            )
        )
        
        self.manager = QtWidgets.QStackedLayout(self)

        authContainer = QWidget()

        authLayout = QtWidgets.QVBoxLayout(authContainer)
        authLayout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        authLayout.setContentsMargins(32,0,432,48)
        authLayout.setSpacing(32)

        vLayout = QtWidgets.QVBoxLayout()
        vLayout.setSpacing(8)

        title = QtWidgets.QLabel(
            text = 'Cинхронизироваться!',
            objectName = 'title',
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum,QtWidgets.QSizePolicy.Policy.Maximum)
        )
        title.setObjectName('title')

        
        mail = LineEdit(
            objectName = 'input',
            placeholderText = 'введите почту'
        )
        mail.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Maximum))
        mail.instance().setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Expanding))

        password = LineEdit(
            objectName = 'input',
            placeholderText = 'введите пароль',
        )
        password.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Maximum))
        password.instance().setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Expanding))

        password.instance().setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        
        action = QtGui.QAction(QtGui.QIcon(Icons().eye),'Show Password',self)
        action.toggled.connect(lambda checked, instance = password:self.togglePassword(checked, instance))
        action.setObjectName('echo')
        action.setCheckable(True)
        action.setChecked(True)
        

        password.instance().addAction(action,QtWidgets.QLineEdit.ActionPosition.TrailingPosition)

        self.confirm = LineEdit(
            objectName = 'input',
            placeholderText = 'повторите пароль'
        )
        self.confirm.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Maximum))
        self.confirm.instance().setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Expanding))

        action = QtGui.QAction(QtGui.QIcon(Icons().eye),'Show Password',self)
        action.toggled.connect(lambda checked, instance = self.confirm:self.togglePassword(checked, instance))
        action.setObjectName('echo')
        action.setCheckable(True)
        action.setChecked(True)

        self.confirm.instance().addAction(action, QtWidgets.QLineEdit.ActionPosition.TrailingPosition)
        
        submit = Button(
            objectName = 'button',
            text = 'Подтвердить'
        )
        submit.setShadowColor(Theme.shadow)
        submit.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Maximum))
        submit.instance().setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Expanding))
        submit.instance().clicked[bool].connect(lambda checked, username = mail.instance(), 
                                                password = password.instance(), 
                                                confirm = self.confirm.instance() : self.submit(
            username, password, confirm
        ))
        submit.instance().setCheckable(False)
        
        vLayout.addWidget(title)
        vLayout.addWidget(mail)
        vLayout.addWidget(password)
        vLayout.addWidget(self.confirm)
        vLayout.addWidget(submit)

        authLayout.addLayout(vLayout)

        vLayout = QtWidgets.QVBoxLayout()
        vLayout.setSpacing(8)

        self.toggleTitle = QtWidgets.QLabel(
            objectName = 'title',
        )
        self.toggleTitle.setStyleSheet('font-size:{h2}'.format(h2 = Metrics.h2))

        self.toggleButton = Button()
        self.toggleButton.instance().setStyleSheet('background:#EDEDED')
        self.toggleButton.setShadowFill(True)
        self.toggleButton.instance().clicked.connect(lambda * args:self.toggleType())

        self.toggleButton.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Maximum))
        self.toggleButton.instance().setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Expanding))


        vLayout.setContentsMargins(0,0,0,0)
        vLayout.addWidget(self.toggleTitle)
        vLayout.addWidget(self.toggleButton)

        authLayout.addLayout(vLayout)

        self.toggleType(self.Type.AUTHENTICATION)

        self.manager.addWidget(authContainer)


        
        userContainter = QWidget()
        hLayout = QtWidgets.QHBoxLayout(userContainter)


        con = Widget(objClass=QWidget)

        # con.instance().setStyleSheet(f'background:{Theme.window}')
        # con.setShadowFill(True)
        con.setSizePolicy(QSizePolicy(
            QSizePolicy.Policy.Maximum,QSizePolicy.Policy.Maximum
        ))
        con.instance().setSizePolicy(QSizePolicy(
            QSizePolicy.Policy.Maximum,QSizePolicy.Policy.Maximum
        ))
        vLayout = QtWidgets.QVBoxLayout(con.instance())
        vLayout.setContentsMargins(8,32,8,32)
        vLayout.setSpacing(24)

        self.userTitle = QLabel()
        self.userTitle.setStyleSheet(f'font-weight:900;font-size:{Metrics.h1}')
        self.userTitle.setSizePolicy(QSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum
        ))
        
        btn = Button(text = 'Выйти')
        btn.setSizePolicy(QSizePolicy(
            QSizePolicy.Policy.Maximum,QSizePolicy.Policy.Maximum
        ))
        btn.instance().setSizePolicy(QSizePolicy(
            QSizePolicy.Policy.Maximum,QSizePolicy.Policy.Maximum
        ))
        btn.instance().setStyleSheet(f'background:{Theme.secondaryColor};padding:12px 36px')
        btn.setShadowFill(True)
        btn.instance().clicked.connect(self.logout)

        vLayout.addWidget(self.userTitle, alignment=Qt.AlignmentFlag.AlignCenter)
        vLayout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        
        hLayout.addWidget(con)

        self.manager.addWidget(userContainter)

        # self.controller.onStart()
    def togglePassword(self, show, instance):
        if show:
            instance.instance().setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
            for action in instance.instance().actions():
                if action.objectName() == 'echo':
                    action.setIcon(QtGui.QIcon(Icons().eye))
        else:
            instance.instance().setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
            for action in instance.instance().actions():
                if action.objectName() == 'echo':
                    action.setIcon(QtGui.QIcon(Icons().eye_off))

    def toggleType(self, _t:Type = None):
        if _t != None:
            self.type = _t

        else:
            if self.type == self.Type.AUTHENTICATION:
                self.type = self.Type.REGISTRATION
            else:
                self.type = self.Type.AUTHENTICATION
    
    def submit(self, 
               username:QtWidgets.QLineEdit,
               password:QtWidgets.QLineEdit,
               confirm:QtWidgets.QLineEdit):
        if (len(username.text())  == 0 or len(password.text()) < 7) or (
            self.type == self.Type.REGISTRATION and password.text() != confirm.text()):
            u,p,c = username.styleSheet(), password.styleSheet(), confirm.styleSheet()

            QtCore.QTimer().singleShot(1000, lambda u = u, p = p, c = c:(
                username.setStyleSheet(u),
                password.setStyleSheet(p),
                confirm.setStyleSheet(c),
            ))

            username.setStyleSheet(u + f';color:{Theme.primaryError}')
            password.setStyleSheet(p + f';color:{Theme.primaryError}')
            confirm.setStyleSheet(c + f';color:{Theme.primaryError}')
           
        else:
            self.controller.onSubmit(
                username.text(), 
                password.text(), 
                type = 'SIGN_UP' if self.type == self.Type.REGISTRATION else 'SIGN_IN')

    def logout(self):
        self.controller.logout()

    def paintEvent(self, a0: QPaintEvent or None) -> None:
        if self.manager.currentIndex() == 0:
            painter = QtGui.QPainter(self)
            painter.setBrush(QtGui.QColor(Theme.primaryColor))
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(
                self.rect().width() - 400,
                0,
                400,
                self.height()
            )
            pixmap = QtGui.QPixmap(
                Path.image('user_screen_splash.png')
            ).scaled(QtCore.QSize(472,432),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation)
            rect = pixmap.rect()
            rect.moveBottomRight(self.rect().bottomRight())
            painter.drawPixmap(rect, pixmap)
        return super().paintEvent(a0)

    def model_is_changed(self, event:Observer.ObserverEvent, data:dict = None):
        if event.type() == Observer.ObserverEvent.AUTHENTICATION:
            self.manager.setCurrentIndex(1)

            self.userTitle.setText(data['email'])
            
        elif event.type() == Observer.ObserverEvent.LOGOUT:
            self.manager.setCurrentIndex(0)

            self.userTitle.clear()