from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtCore import QSize, Qt

from Utility.path import Path

class Icons(object):
    def __init__(self, size = QSize(32,32), color:str or QColor = QColor('#000000')) -> None:
        self.size = size
        self.color = QColor(color) if isinstance(color, str) else color

    def __load__(self, filename:str)->QPixmap:
       
        image = QPixmap(filename).scaled(
                    self.size, 
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation).toImage()
        
        if isinstance(self.color, QColor):
            for x in range(image.width()):
                for y in range(image.height()):
                    r,g,b,a = image.pixelColor(x,y).getRgb()
                    if a > 0:
                        self.color.setAlpha(a)
                        image.setPixelColor(x,y, self.color)

        return QPixmap.fromImage(image)
    
    @property
    def back(self):
        return self.__load__(
            filename=Path.icon('back.png')
        )
    
    @property
    def left_arrow(self):
        return self.__load__(
            filename= Path.icon('left_arrow.png'),
        )
    @property
    def right_arrow(self):
        return self.__load__(
            filename=Path.icon('right_arrow.png'),
        )
    @property
    def eye_off(self):
        return self.__load__(
            filename = Path.icon('eye_off.png'),
        )
    @property
    def eye(self):
        return self.__load__(
            filename = Path.icon('eye.png'),
        )
    @property
    def map(self):
        return self.__load__(
            filename = Path.icon('map_sign.png'),
        )
    @property
    def coins(self):
        return self.__load__(
            filename= Path.icon('coins.png'),
        )
    @property
    def room(self):
        return self.__load__(
            filename= Path.icon('room.png'),
        )
    @property
    def time(self):
        return self.__load__(
            filename=Path.icon('time.png'),
        )
    @property
    def checkmark(self):
        return self.__load__(
            filename = Path.icon('checkmark.png')
        )
    
    @property
    def refresh(self):
        return self.__load__(
            filename = Path.icon('refresh.png')
        )
    @property
    def avito(self):
        return self.__load__(
            filename=Path.icon('avito.png'),
        )
    @property
    def cian(self):
        return self.__load__(
            filename=Path.icon('cian.png'),
        )
    @property
    def plus(self):
        return self.__load__(
            filename=Path.icon('plus.png'), 
            )
    @property
    def close(self):
        return self.__load__(
            filename=Path.icon('close.png'),
        )
    @property
    def filter(self):
        return self.__load__(
            filename=Path.icon('filter.png'),
        )
    @property
    def ads(self):
        return self.__load__(
            filename=Path.icon('ad.png'),
        )
    @property
    def favourite(self):
        return self.__load__(
            filename=Path.icon('favourite.png'),
        )
    @property
    def history(self):
        return self.__load__(
            filename=Path.icon('history.png'),
        )
    @property
    def user(self):
        return self.__load__(
            filename=Path.icon('user.png')
        )

class Metrics(object):
    h1 = '24px'
    h2 = '16px'
    p = '12px'

class Theme(object):
    themeStyle = 'Light'
    window = '#FBF1E5'
    sidebar = '#FFFFFF'
    primaryTextColor = '#000000'
    secondaryTextColor = '#3D3D3D'
    primaryColor = '#EF6262'
    secondaryColor = '#F3AA60'
    shadow = '#000000'
    secondaryShadowColor = '#515151'
    primaryError = primaryColor
    primaryFont = 'Piazzolla'
    
class Style(object):

    border_radius = '20'
    border_width = '3px'
    shadowXOffset = 6
    shadowYOffset = 8
    sheet = '''
QMainWindow{{
    background-color:{window};
}}
#filterBar{{
    background:{primaryColor};
    border-left:{border_width} solid {shadow};
}}
#shadow{{

}}
#input{{
    background:transparent;
    border-style:solid;
    border-color:black;
    border-width:4;
    border-radius:{border_radius};
    color:#3D3D3D;
    font-weight:900;
}}
#input:focus{{
    background:#F3AA60;
}}

#filter{{
    background-color:#EF6262;
    border-left:4px solid black;
}}
#comment{{
    border-style:dashed;
    border-width:4;
    border-color:#828282;
    border-radius:{border_radius};
    background-color:rgba(217,217,217,.31);
    padding:10px;
    font-weight:bold;
}}

#comment:focus{{
    border-style:solid;
    border-color:'black';
    background-color:#F3AA60;
}}

QLabel#notification{{
    font-size: 40px;
    color: #EF6262;
    font-weight: 900;
}}
QWidget{{
    font-family:Piazzolla;
}}
QLabel{{
    font-family:Piazzolla;   
    font-weight:200;
}}
QPushButton{{
    font-family:Piazzolla;
}}
QLineEdit{{
    font-family:Piazzolla;
}}
'''.format(
        border_radius = border_radius,
        window = Theme.window,
        primaryColor = Theme.primaryColor,
        border_width = border_width,
        shadow = Theme.shadow
)