import sys
from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtGui import QPainter, QPainterPath, QPen, QColor, QBrush
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsRectItem


from Objects2D import *
from ReaderDXF import load_mp, create_msp


def my_excepthook(type, value, tback):
    QtWidgets.QMessageBox.critical(
        window, "CRITICAL ERROR", str(value),
        QtWidgets.QMessageBox.Cancel
    )
    sys.__excepthook__(type, value, tback)


class MyItem(QtWidgets.QGraphicsItem):
    def __init__(self, obj: DxfObject):
        super().__init__()
        self.obj = obj
        self.rect = obj.get_rect
        # self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(*self.rect)

    def paint(self, painter: QtGui.QPainter, option, widget) -> None:
        if sum(self.rect) > 0:
            self.setTransform(QtGui.QTransform.fromScale(1, -1))

            # if self.obj.__dict__.get('alpha'):      # Для дуг
            #     self.obj: EllipseArc
            #     x, y = self.obj.center.x, self.obj.center.y
            #     transform = QtGui.QTransform().translate(x, -y).rotate(self.obj.alpha).translate(-x, -y)
            #     self.setTransform(transform)
            if self.obj.__dict__.get('text'):       # Для текста
                self.setTransform(QtGui.QTransform.fromScale(1, 1))

            self.obj.draw(painter)

            # pen = QPen(QColor(255, 0, 255), 0.5)
            # pen.setWidthF(1.0 / painter.transform().m11())
            # painter.setPen(pen)
            # painter.drawRect(self.boundingRect())

    def mousePressEvent(self, event) -> None:
        super().mousePressEvent(event)
        # painter = QPainter()
        # painter.begin(self)
        # pen = QPen(QColor(255, 0, 255), 0.5)
        # pen.setWidthF(1.0 / painter.transform().m11())
        # painter.setPen(pen)
        # painter.drawRect(self.boundingRect())
        # painter.end()
        # print(self.obj)


class Scene(QtWidgets.QGraphicsScene):
    def __init__(self, msp: ModelSpace):
        super().__init__()
        r = 2000
        # self.setSceneRect(-150, -150, 500, 150)
        self.msp = msp
        self.fillScene()

    def fillScene(self):
        self.setBackgroundBrush(QBrush(QColor(255, 0, 0)))
        for obj in self.msp:
            # if isinstance(obj, EllipseArc):
                # obj.center *= Vec2(1, -1)
            item = MyItem(obj)
            # item.setTransform(QtGui.QTransform.fromScale(1, -1))
            # if isinstance(obj, EllipseArc):
            #     item.setTransform(QtGui.QTransform.fromScale(1, 1))
                # item.y *= -1

            # if obj.__dict__.get('text'):
            #     item.setTransform(QtGui.QTransform.fromScale(1, 1))
            self.addItem(item)

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        pen = QPen(QColor(0, 255, 0), 5)
        bruh = QBrush(QColor(0, 255, 0))
        painter.setPen(pen)
        painter.setBrush(bruh)
        painter.drawRect(self.sceneRect())


class GraphicsView(QtWidgets.QGraphicsView):
    def __init__(self, parent, msp: ModelSpace):
        super().__init__(parent)
        self.scene = Scene(msp)
        # self.setSceneRect(-150, -150, 0, 0)
        self.setScene(self.scene)
        self.scale(2, 2)

        self.__old_pos = None
        self.flag_move = False
        # self.setSceneRect(-2000, -2000, 0, 0)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(50, 50, 50)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        # self.setDragMode(1)
        # self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            # self.setDragMode(QGraphicsView.NoDrag)
            self.flag_move = True
            self.__old_pos = event.pos()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.flag_move:
            delta = event.pos() - self.__old_pos
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self.__old_pos = event.pos()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            # self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.flag_move = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        scalefactor = 1.5
        if event.angleDelta().y() > 0:
            self.scale(scalefactor, scalefactor)
        else:
            self.scale(1/scalefactor, 1/scalefactor)


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initWindow()

        # self.dxf_file = r'dxf_files/block.dxf'
        self.dxf_file = r'dxf_files/Зона_101_Отделение_приёмки_сырого_молока_03_02_23.dxf'
        self.msp = self.get_msp()

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        vl = QtWidgets.QGridLayout(self.centralwidget)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(5)

        btn_1 = QtWidgets.QPushButton(self.centralwidget )
        btn_1.clicked.connect(self.update_msp)
        btn_1.setText('Обновить')
        vl.addWidget(btn_1)

        self.graphics = GraphicsView(self, self.msp)
        self.graphics.resize(self.size())
        vl.addWidget(self.graphics)

        self.setCentralWidget(self.centralwidget)

    def initWindow(self) -> None:
        self.resize(600, 600)
        self.setWindowTitle('Window')

    def get_msp(self) -> ModelSpace:
        return create_msp(self.dxf_file)

    def update_msp(self, event) -> None:
        self.msp = self.get_msp()
        self.graphics.scene.clear()
        self.graphics.scene.msp = self.msp
        self.graphics.scene.fillScene()

    # def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
    #     super(Window, self).resizeEvent(event)
        # self.graphics.resize(self.width(), self.height())


if __name__ == '__main__':
    # sys.excepthook = my_excepthook

    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
