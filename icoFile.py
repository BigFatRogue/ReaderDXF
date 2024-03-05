import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PIL import Image
import io


def get_preview_file(filepath):
    with open(filepath, 'rb') as fin:
        sourcedata = fin.read()
    print(sourcedata)
    start = sourcedata.index(b'\x89PNG')
    end = sourcedata.index(b'IEND\xaeB`\x82')

    byte_arr = sourcedata[start: end + len(b'IEND\xaeB`\x82') ]

    return byte_arr


class DragLabel(QtWidgets.QLabel):
    signal_selected_file_label = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.initLabel()

    def initLabel(self):
        font = QtGui.QFont()
        font.setPointSize(14)
        self.setFont(font)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.setStyleSheet("QLabel {\n"
                           "    background-color:rgb(59, 68, 83);\n"
                           "    border-radius: 15px;\n"
                           "    border:  2px dashed black;\n"
                           "     color: white;\n"
                           "}\n"
                           "QLabel::hover {background-color:rgba(46, 52, 64, 150)}\n"
                           "\n"
                           "")
        self.setTextFormat(QtCore.Qt.PlainText)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setObjectName("label")
        self.setText(f"Выберете или \nперетащите файл")

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        super(DragLabel, self).dragEnterEvent(event)
        event.accept()
        # if event.mimeData().hasUrls():
        #     lst_files = event.mimeData().urls()
        #

    def dropEvent(self, event: QtGui.QDragEnterEvent):
        for url in event.mimeData().urls():
            filepath = url.toLocalFile()
            self.signal_selected_file_label.emit(filepath)
            event.accept()


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initWindow()
        self.initWidgets()

    def initWindow(self):
        self.resize(400, 200)
        self.setWindowTitle('Window')

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.mainLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(5)

        self.setCentralWidget(self.centralwidget)

    def initWidgets(self):
        self.label_image = QtWidgets.QLabel(self)
        # self.label_image.setMaximumSize(200, 200)
        self.label_image.setStyleSheet('QLabel {background-color:rgb(50, 255, 50);}')
        self.mainLayout.addWidget(self.label_image)

        self.label = DragLabel(self)
        self.label.signal_selected_file_label.connect(self.fillLabel)
        self.mainLayout.addWidget(self.label)

        # try:
        #     pixmap = QtGui.QPixmap()
        #     pixmap.loadFromData(get_preview_file(r'C:\Users\TORTIK\Downloads\Telegram Desktop\Новая папка\Clamp. Хомут DIN11850.ipt'))
        #     pixmap.scaled(150, 150)
        #     self.label_image.setPixmap(pixmap)
        # except Exception:
        #     pass

    def fillLabel(self, filepath):
        try:
            pixmap = QtGui.QPixmap()
            image = get_preview_file(filepath)
            pixmap.loadFromData(image)
            pixmap.scaled(150, 150)
            self.label_image.setPixmap(pixmap)

            with open('img.png', 'wb') as img:
                img.write(image)
        except Exception:
            pass


if __name__ == '__main__':
    # filepath = r'C:\Users\TORTIK\Downloads\Telegram Desktop\Новая папка\МС Гайка накидная DIN11850-.ipt'
    # image = get_preview_file(filepath)
    #
    # with open('img.png', 'wb') as img:
    #     img.write(image)
    # #
    # Image.frombytes('RGBA', (150, 150), image).show()
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())

