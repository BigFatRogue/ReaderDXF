from PyQt5 import QtGui
from PyQt5.QtGui import QPainter, QPainterPath, QPen, QColor, QBrush
from PyQt5.QtCore import QPointF, QRectF
import math


class Vec2:
    def __init__(self, x: float, y: float):
        self.__x = x
        self.__y = y
        self.__cor = (x, y)

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def coords(self):
        return self.__cor

    def __add__(self, other):
        if isinstance(other, Vec2):
            return Vec2(self.__x + other.x, self.__y + other.y)
        elif isinstance(other, (float, int)):
            return Vec2(self.__x + other, self.__y + other)
        raise 'Прибавлять можно только объект Vec2, int или float'

    def __radd__(self, other):
        return self + other

    def __iadd__(self, other):
        if isinstance(other, Vec2):
            self.__x += other.x
            self.__y += other.y
            return Vec2(self.__x, self.__y)
        elif isinstance(other, (float, int)):
            self.__x += other
            self.__y += other
            return Vec2(self.__x, self.__y)
        raise 'Прибавлять можно только объект Vec2, int или float'

    def __sub__(self, other):
        if isinstance(other, Vec2):
            return Vec2(self.__x - other.x, self.__y - other.y)
        elif isinstance(other, (float, int)):
            return Vec2(self.__x - other, self.__y - other)
        raise 'Вычитать можно только объект Vec2, int или float'

    def __rsub__(self, other):
        return self - other

    def __isub__(self, other):
        if isinstance(other, Vec2):
            self.__x -= other.x
            self.__y -= other.y
            return Vec2(self.__x, self.__y)
        elif isinstance(other, (float, int)):
            self.__x -= other
            self.__y -= other
            return Vec2(self.__x, self.__y)
        raise 'Прибавлять можно только объект Vec2, int или float'

    def __mul__(self, other):
        if isinstance(other, Vec2):
            return Vec2(self.x * other.x, self.y * other.y)
        elif isinstance(other, (float, int)):
            return Vec2(self.x * other, self.y * other)
        raise 'Перемножать можно только с объектами Vec2, int или float'

    def __rmul__(self, other):
        return self * other

    def __imul__(self, other):
        if isinstance(other, Vec2):
            self.__x *= other.x
            self.__y *= other.y
            return Vec2(self.__x, self.__y)
        elif isinstance(other, (float, int)):
            self.__x *= other
            self.__y *= other
            return Vec2(self.__x, self.__y)
        raise 'Перемножать можно только с объектами Vec2, int или float'

    def __truediv__(self, other):
        if isinstance(other, Vec2):
                return Vec2(self.x / other.x, self.y / other.y)
        elif isinstance(other, (float, int)):
            return Vec2(self.x / other, self.y / other)
        raise 'Делить можно только на объекты Vec2, int или float'

    def __rtruediv__(self, other):
        return self / other

    def __itruediv__(self, other):
        if isinstance(other, Vec2):
            self.__x /= other.x
            self.__y /= other.y
            return Vec2(self.__x, self.__y)
        elif isinstance(other, (float, int)):
            self.__x /= other
            self.__y /= other
            return Vec2(self.__x, self.__y)
        raise 'Делить можно только на объекты Vec2, int или float'

    def __abs__(self):
        return Vec2(abs(self.__x), abs(self.__y))

    def angle_between(self, *args) -> float:
        other = None
        if len(args) == 1:
            x1, y1 = args[0].x, args[0].y
        elif len(args) == 2:
            x1, y1 = args
        else:
            raise 'Аргумент должен быть либо (float, float), либо Vec2'

        ab = self.x * x1 + self.y * y1
        len_a = math.sqrt(self.x**2 + self.y**2)
        len_b = math.sqrt(x1**2 + y1**2)

        # k = -1 if self.x < 0 or self.y < 0 or other.x < 0 or other.y else 1

        if len_a == 0 or len_b == 0:
            return 0
        return math.acos(ab / (len_a * len_b)) * 180 / math.pi

    def __len__(self):
        return self.len()

    def len(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def __getitem__(self, item):
        if type(item) == int:
            return self.__cor[item]

    def __str__(self):
        return f'({self.__x}, {self.__y})'

    def __repr__(self):
        return self.__str__()


class DxfObject:
    def __init__(self, scale=None, color=None, lineweight=None):
        self.__id = None

        if color is None:
            self.color = QColor('white')
        elif isinstance(color, (int, str)):
            self.color = QColor(color)
        else:
            self.color = QColor(*color)

        self.lineweight = lineweight
        self.scale = Vec2(1, 1) if scale is None else scale

    @property
    def id(self) -> int:
        return self.__id

    @id.setter
    def id(self, value):
        self.__id = value

    def correct_coords(self, dx: float, dy: float) -> None:
        ...

    def draw(self, *args, **kwargs) -> None:
        ...

    @property
    def get_rect(self) -> tuple:
        return 0, 0, 0, 0

    @property
    def type(self) -> str:
        return self.__class__.__name__

    def __str__(self):
        return f'({self.__class__.__name__}, id: {self.id})'

    def __repr__(self):
        return self.__str__()


class Line(DxfObject):
    def __init__(self, pos0: tuple, pos1: tuple, scale: Vec2, linetype: str, color: [int, str, tuple, list],
                 lineweight: float):
        super().__init__(scale, color, lineweight)
        self.__pos0 = Vec2(*pos0) * self.scale
        self.__pos1 = Vec2(*pos1) * self.scale

        self.linetype = linetype
        self.__rect = self.__get_rect()

    def correct_coords(self, dx, dy):
        dVec = Vec2(dx, dy)
        self.__pos0 += dVec
        self.__pos1 += dVec
        self.__rect = self.__get_rect()

    def draw(self, painter: QtGui.QPainter, pen=None, bruh=None):
        pen = QPen(self.color, self.lineweight)
        pen.setWidthF(1.0 / painter.transform().m11())
        bruh = QBrush(QColor(0, 0, 0, 0))

        painter.setPen(pen)
        painter.setBrush(bruh)
        painter.drawLine(QPointF(*self.__pos0), QPointF(*self.__pos1))

    def __get_rect(self) -> tuple:
        return *self.__pos0, *(self.__pos1 - self.__pos0)

    @property
    def get_rect(self):
        return self.__rect

    @property
    def get_pos0(self):
        return self.__pos0

    @property
    def get_pos1(self):
        return self.__pos1

    def __str__(self):
        return f'({self.__class__.__name__}, id: {self.id}, pos0: {self.__pos0}, pos1: {self.__pos1})'

    def __repr__(self):
        return self.__str__()


class Polyline(DxfObject):
    def __init__(self):
        super().__init__()

        self.__objects = []
        self.__rect = None

    def add_object(self, obj: DxfObject) -> None:
        self.__objects.append(obj)

    def correct_coords(self, dx, dy):
        for obj in self.__objects:
            obj.correct_coords(dx, dy)

    def draw(self, painter: QtGui.QPainter, pen=None, bruh=None):
        pen = QPen(QColor(255, 255, 0), 0.5)
        pen.setWidthF(1.0 / painter.transform().m11())
        bruh = QBrush(QColor(0, 0, 0, 0))
        painter.setPen(pen)
        painter.setBrush(bruh)

        for obj in self.__objects:
            obj.draw(painter=painter)

    def __get_rect(self):
        rects = [obj.get_rect for obj in self.__objects]

        xx_min = [i[0] for i in rects]
        yy_min = [i[1] for i in rects]
        xx_max = [i[0] + i[2] for i in rects]
        yy_max = [i[1] + i[3] for i in rects]
        x, y = min(xx_min), min(yy_min)
        w, h = max(xx_max) - x, max(yy_max) - y

        return x, y, w, h

    @property
    def get_rect(self) -> tuple:
        if self.__rect is None:
            self.__rect = self.__get_rect()
        return self.__rect

    @property
    def get_objects(self):
        return self.__objects

    def __getitem__(self, item: int) -> DxfObject:
        if item < len(self.__objects):
            return self.__objects[item]
        raise IndexError

    def __setitem__(self, item: int, obj: DxfObject) -> None:
        if item < len(self.__objects):
            self.__objects[item] = obj
        else:
            raise IndexError

    def __str__(self):
        return f'({self.__class__.__name__}, id: {self.id}, count_line: {len(self.__objects)})'

    def __repr__(self):
        return self.__str__()


class Circle(DxfObject):
    def __init__(self, center: tuple, radius: float, scale: Vec2, color: (int, str), lineweight: int):
        super().__init__(scale, color, lineweight)
        self.center = Vec2(*center) * self.scale
        self.w = radius * 2 * self.scale.x
        self.h = radius * 2 * self.scale.y

        self.radius = radius
        self.__rect = self.__get_rect()

    def correct_coords(self, dx, dy):
        dVec = Vec2(dx, dy)
        self.center += dVec
        self.__rect = self.__get_rect()

    def __get_rect(self) -> tuple:
        return self.center.x - self.radius, self.center.y - self.radius, self.w, self.h

    @property
    def get_rect(self) -> tuple:
        return self.__rect

    def draw(self, painter: QtGui.QPainter, pen=None, bruh=None) -> None:
        pen = QPen(QColor(self.color), 0.5)
        pen.setWidthF(1.0 / painter.transform().m11())
        bruh = QBrush(QColor(0, 0, 0, 0))
        painter.setPen(pen)
        painter.setBrush(bruh)

        painter.drawEllipse(QRectF(*self.__get_rect()))

    def __str__(self):
        return f'({self.__class__.__name__}, id: {self.id}, centre: {self.center}, radius: {self.radius})'

    def __repr__(self):
        return self.__str__()


class Acr(DxfObject):
    def __init__(self, center: tuple, radius: float, start_angle: float, end_angle: float, scale: Vec2,
                 color: int, lineweight: int, pos0=None):
        super().__init__(scale, color, lineweight)
        self.center = Vec2(*center)
        self.radius = radius
        self.start_angle = int(start_angle)
        self.end_angle = int(end_angle)
        self.__pos0 = pos0

        self.__rect = self.__get_rect()

    def correct_coords(self, dx, dy):
        dVec = Vec2(dx, dy)
        self.center += dVec
        self.__rect = self.__get_rect()

    def __get_rect(self) -> tuple:
        return self.center.x - self.radius, self.center.y - self.radius, self.radius * 2, self.radius * 2

    @property
    def get_rect(self) -> tuple:
        return self.__rect

    @property
    def get_arc(self) -> tuple:
        return self.center, self.radius, self.start_angle, self.end_angle

    @property
    def get_pos0(self):
        return self.__pos0

    def draw(self, painter: QtGui.QPainter, pen=None, bruh=None):
        pen = QPen(QColor(255, 255, 0), 0.5)
        pen.setWidthF(1.0 / painter.transform().m11())
        bruh = QBrush(QColor(0, 0, 0, 0))
        painter.setPen(pen)
        painter.setBrush(bruh)
        len_arc = abs(self.end_angle - self.start_angle)
        len_arc = 360 - len_arc if self.end_angle < self.start_angle else len_arc
        painter.drawArc(QRectF(*self.__get_rect()), -self.start_angle * 16, -len_arc * 16)

    def __str__(self):
        return f'({self.__class__.__name__}, id: {self.id}, centre: {self.center}, radius: {self.radius}, s_angle: {self.start_angle}, e_angle: {self.end_angle})'

    def __repr__(self):
        return self.__str__()


class Ellipse(DxfObject):
    def __init__(self, center: tuple, w: float, h: float, alpha: float, scale: Vec2, color: int, lineweight: int):
        super().__init__(scale, color, lineweight)
        self.center = Vec2(*center) * self.scale
        self.w, self.h = w * self.scale.x, h * self.scale.y
        self.alpha = alpha

        self.__rect = self.__get_rect()

    def correct_coords(self, dx, dy):
        dVec = Vec2(dx, dy)
        self.center += dVec
        self.__rect = self.__get_rect()

    def __get_rect(self) -> tuple:
        return self.center.x - self.h, self.center.y - self.w, self.h * 2, self.w * 2

    @property
    def get_rect(self) -> tuple:
        return self.__rect

    def draw(self, painter: QtGui.QPainter, pen=None, bruh=None):
        pen = QPen(QColor(255, 255, 0), 0.5)
        try:
            pen.setWidthF(1.0 / painter.transform().m11())
        except ZeroDivisionError:
            pass

        bruh = QBrush(QColor(0, 0, 0, 0))
        painter.setPen(pen)
        painter.setBrush(bruh)
        painter.drawEllipse(QRectF(*self.__rect))

    def __str__(self):
        return f'({self.__class__.__name__}, id: {self.id}, center: {self.center}, w: {self.w}, h: {self.h}, alpha: {self.alpha})'

    def __repr__(self):
        return self.__str__()


class Text(DxfObject):
    def __init__(self, coord: tuple, text: str, height: float, color: int):
        super().__init__()
        self.x, self.y = self.coord = coord
        self.text = self.__preprocessing_text(text)
        self.height = height
        self.color = color

        self.__rect = self.__get_rect()

    def correct_coords(self, dx, dy):
        self.x += dx
        self.y += dy

    def __preprocessing_text(self, text: str) -> str:
        return text.replace('\P', '\n')

    def __get_rect(self):
        return self.x, self.y, len(self.text) * 4, self.height*10

    @property
    def get_rect(self) -> tuple:
        return self.__rect

    def draw(self, painter: QtGui.QPainter, pen=None, bruh=None):
        pen = QPen(QColor(255, 255, 0), 0.5)
        pen.setWidthF(1.0 / painter.transform().m11())
        bruh = QBrush(QColor(0, 0, 0, 0))
        painter.setPen(pen)
        painter.setBrush(bruh)
        painter.drawText(QRectF(*self.__rect), 3, self.text)

    def __str__(self):
        return f'({self.__class__.__name__}, id: {self.id}, coord: {self.coord})'

    def __repr__(self):
        return self.__str__()


class Block(DxfObject):
    def __init__(self, coord: tuple, name: str):
        super().__init__()
        self.x, self.y = self.coord = coord

        self.name = name
        self.__attributes = {}
        self.__objects = []
        self.__rect = None

    def add_attribute(self, key: str, value: str):
        self.__attributes[key] = value

    def add_object(self, obj: DxfObject) -> None:
        obj.correct_coords(self.x, self.y)
        self.__objects.append(obj)

    def __get_rect(self) -> tuple:
        rects = [obj.get_rect for obj in self.__objects if sum(obj.get_rect) != 0]

        xx_min = [i[0] for i in rects]
        yy_min = [i[1] for i in rects]
        xx_max = [i[0] + i[2] for i in rects]
        yy_max = [i[1] + i[3] for i in rects]
        if all(len(i) > 0 for i in (xx_max, yy_min, xx_max, yy_max)):
            x, y = min(xx_min), min(yy_min)
            w, h = max(xx_max) - x, max(yy_max) - y
        else:
            x, y, w, h, = 0, 0, 0, 0
        return x, y, w, h

    @property
    def get_rect(self) -> tuple:
        if self.__rect is None:
            self.__rect = self.__get_rect()
        return self.__rect

    def correct_coords(self, dx, dy):
        self.x, self.y = self.coord = self.x - dx, self.y - dy
        for obj in self.__objects:
            obj.correct_coords(dx, dy)
        self.__rect = self.__get_rect()

    def draw(self, painter: QtGui.QPainter, pen=None, bruh=None):
        for obj in self.__objects:
            obj.draw(painter=painter)

    @property
    def get_objects(self) -> list:
        return self.__objects

    @property
    def get_attributes(self) -> dict:
        return self.__attributes

    def __str__(self):
        return f'({self.__class__.__name__}, id: {self.id}, name: {self.name}, coord: {self.coord})'

    def __repr__(self):
        return self.__str__()


class EllipseArc(DxfObject):
    def __init__(self, center: tuple, w: float, h: float, alpha: float, start_angle: float, len_arc: float,
                 scale: Vec2, color: int, lineweight: float):
        super().__init__(scale, color, lineweight)

        self.center = Vec2(*center) * self.scale
        self.w, self.h = w * self.scale.x, h * self.scale.y
        self.start_angle = start_angle
        self.len_arc = len_arc
        self.alpha = alpha
        self.__rect = self.__get_rect()

    def correct_coords(self, dx, dy):
        dVec = Vec2(dx, dy)
        self.center += dVec
        self.__rect = self.__get_rect()

    def __get_rect(self) -> tuple:
        return self.center.x - self.h, self.center.y - self.w, self.h * 2, self.w * 2

    @property
    def get_rect(self) -> tuple:
        return self.__rect

    def draw(self, painter: QtGui.QPainter, pen=None, bruh=None):
        pen = QPen(self.color, 0.5)
        try:
            pen.setWidthF(1.0 / 10)
        except ZeroDivisionError:
            pass

        bruh = QBrush(QColor(0, 0, 0, 0))
        painter.setPen(pen)
        painter.setBrush(bruh)
        painter.save()

        x, y = self.center.x, self.center.y
        painter.translate(x, y)
        painter.rotate(-self.alpha)
        painter.translate(-x, -y)

        painter.drawArc(QRectF(*self.__get_rect()), int(self.start_angle * 16), int(self.len_arc * 16))
        painter.restore()


    def __str__(self):
        return f'({self.__class__.__name__}, id: {self.id}, center: {self.center}, w: {self.w}, h: {self.h}, alpha: {self.alpha}, ' \
               f'start_angle: {self.start_angle})'

    def __repr__(self):
        return self.__str__()


class ModelSpace:
    __instance = None
    __count_object = 0

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            return super().__new__(cls)
        return cls.__instance

    def __init__(self):
        self.__elements: list[DxfObject] = []
        self.__all_coords = []

    def add(self, obj: [DxfObject, list, tuple]) -> None:
        if isinstance(obj, DxfObject):
            lst = (obj, )
        else:
            lst = obj
        for i in lst:
            i.id = self.__count_object
            self.__elements.append(i)
            self.__all_coords.append(i.get_rect[:2])
            self.__count_object += 1

        # obj.id = self.__count_object
        # self.__elements.append(obj)
        # self.__all_coords.append(obj.get_rect[:2])
        # self.__count_object += 1

    def correct_coords(self) -> None:
        min_xy = sorted(self.__all_coords, key=lambda cor: (cor[0], cor[1]))

        for obj in self.__elements:
            obj.correct_coords(*min_xy[0])

    def __len__(self):
        return len(self.__elements)

    def __getitem__(self, item: (int, str)) -> (DxfObject, tuple):
        if isinstance(item, int):
            return self.__elements[item]
        return tuple(i for i in self.__elements if i.type == item)

    def __str__(self):
        return f'{self.__elements}'


if __name__ == '__main__':
    O = Vec2(0, 0)
    p = Vec2(5, 5)
    vec = p - O

    fi = math.radians(45 + 30)

    x1, y1 = vec.len() * math.cos(fi), vec.len() * math.sin(fi)
    print(x1, y1)


