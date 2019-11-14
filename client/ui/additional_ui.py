""" Module implements addinional widgets """
import re
import os

from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QBuffer, QIODevice, QSize, QRect, QPoint
from PyQt5.Qt import QSizePolicy, QFrame, QAbstractScrollArea, QRubberBand
from PyQt5.QtGui import QPixmap, QIcon, QFont, QTextCursor, QImage
from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QFileDialog, \
                            QGridLayout, QHBoxLayout, QListWidgetItem, \
                            QLabel, QPushButton, QTextBrowser, QTextEdit, QComboBox
from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt

from ui.login_ui import Ui_Dialog as LoginDialog
from ui.image_filters_ui import Ui_Dialog as ImageFilterDialog


class UserWidget(QWidget):
    """ Class the widget of list item to display user """

    def __init__(self, username, avatar_bytes,
                 action_name, action, parent=None):
        super().__init__(parent)
        self.ui()
        self.userLbl.setText(username)
        self.username = username
        self.actinBtn.setText(action_name)
        self.actinBtn.clicked.connect(action)
        self.set_avatar(avatar_bytes)

    def ui(self):
        """ Method build ui """

        # self.resize(200, 50)
        box = QHBoxLayout(self)
        self.setLayout(box)

        self.avatarLbl = QLabel(self)
        self.avatarLbl.setMinimumSize(QSize(50, 50))
        self.avatarLbl.setMaximumSize(QSize(50, 50))
        self.avatarLbl.setFrameShape(QFrame.Box)

        self.userLbl = QLabel(self)
        self.actinBtn = QPushButton(self)
        self.actinBtn.setFixedSize(50, 25)

        box.addWidget(self.avatarLbl)
        box.addWidget(self.userLbl)
        box.addWidget(self.actinBtn)

    def set_avatar(self, avatar_bytes):
        if avatar_bytes:
            img = QImage.fromData(avatar_bytes)
            self.avatarLbl.setPixmap(QPixmap.fromImage(img))
            self.avatarLbl.setFrameShape(QFrame.NoFrame)


class MessageWidget(QWidget):
    """ Class the widget of list item to display message in chat """

    FORMAT_PATTERN = {
        r'\*\*(.+)\*\*': r'<b>\1</b>',
        '__(.+)__': r'<u>\1</u>',
        '##(.+)##': r'<i>\1</i>',
    }

    def __init__(self, user, text, time, parent=None):
        super().__init__(parent)
        self.ui()

        self.userLbl.setText(user)
        self.timeLbl.setText(time)
        self.set_text(self.apply_format(text))
        # self.msgLbl.setHtml(text)

    def ui(self):
        """ Method build ui """
        grid = QGridLayout(self)
        self.setLayout(grid)

        self.userLbl = QLabel(self)
        self.timeLbl = QLabel(self)
        self.timeLbl.setAlignment(Qt.AlignRight)

        self.line_1 = QFrame(self)
        self.line_1.setFrameShape(QFrame.HLine)
        self.line_1.setFrameShadow(QFrame.Sunken)
        self.line_2 = QFrame(self)
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.msgLbl = QTextBrowser(self)
        # font = QFont()
        # font.setPointSize(12)
        # self.msgLbl.setFont(font)
        self.msgLbl.setFrameShape(QFrame.NoFrame)
        self.msgLbl.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.msgLbl.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.msgLbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        grid.addWidget(self.userLbl, 0, 0)
        grid.addWidget(self.timeLbl, 0, 1)
        grid.addWidget(self.line_1, 1, 0, 1, 2)
        grid.addWidget(self.msgLbl, 2, 0, 1, 2)
        grid.addWidget(self.line_2, 3, 0, 1, 2)

    def set_text(self, text):
        size = self.msgLbl.font().pointSize() * 2
        line_count = len(text.split('<br>'))
        size = size * line_count + 6
        self.msgLbl.setMaximumHeight(size)
        self.msgLbl.setMinimumHeight(size)
        self.msgLbl.setHtml(text)

    def apply_format(self, text):
        text = text.strip()
        text = text.replace('\n', '<br>')
        for pat, fmt in self.FORMAT_PATTERN.items():
            text = re.sub(pat, fmt, text)
        return text


class LoginWindow(QDialog):
    """ Class the login dialog logic """

    def __init__(self, parent=None):
        super().__init__(parent)
        # uic.loadUi(os.path.join(UI_DIR, 'login.ui'), self)
        self.ui = LoginDialog()
        self.ui.setupUi(self)
        self.start = False

        self.ui.loginBtn.setEnabled(False)
        self.ui.usernameTxb.textChanged.connect(self.username_text_changed)
        self.ui.loginBtn.clicked.connect(self.login)
        self.ui.exitBtn.clicked.connect(self.close)

    @property
    def username(self):
        return self.ui.usernameTxb.text()

    @property
    def password(self):
        return self.ui.passwordTxb.text()

    @property
    def ip(self):
        return self.ui.ipAddressTxb.text()

    @ip.setter
    def ip(self, value):
        self.ui.ipAddressTxb.setText(value)

    @property
    def port(self):
        return int(self.ui.portTxb.text())

    @port.setter
    def port(self, value):
        self.ui.portTxb.setText(str(value))

    def username_text_changed(self):
        """ Method the handler of username text field change event """

        if len(self.username) > 2:
            self.ui.loginBtn.setEnabled(True)
        else:
            self.ui.loginBtn.setEnabled(False)

    def login(self):
        """ Method the handler of login button click event """
        self.start = True
        self.close()


class MessageBox(QDialog):
    """ Class the dialog to display system message """

    def __init__(self, messge, parent=None):
        super().__init__(parent)
        self.ui()
        self.errorLbl.setText(messge)

    def ui(self):
        """ Method build ui """
        self.resize(250, 125)
        self.setFixedSize(self.size())
        self.setWindowTitle('Error')

        grid = QGridLayout(self)
        self.setLayout(grid)

        self.errorLbl = QLabel()
        grid.addWidget(self.errorLbl)


class ImageFilter:
    def __init__(self, image_file, size=512):
        self.imageFile = image_file
        self.size = size

    def __load_image(self):
        image = Image.open(self.imageFile)
        s = self.size
        w = image.size[0]
        h = image.size[1]
        if w > h:
            w, h = s, h / w * s
        else:
            h, w = s, w / h * s
        image = image.resize((int(w), int(h)), Image.ANTIALIAS)
        return image

    def get_image(self):
        image = self.__load_image()
        return ImageQt(image.convert('RGBA'))

    def get_sepia(self):
        image = self.__load_image()
        draw = ImageDraw.Draw(image)
        width = image.size[0]
        height = image.size[1]
        pix = image.load()

        depth = 30
        for i in range(width):
            for j in range(height):
                a = pix[i, j][0]
                b = pix[i, j][1]
                c = pix[i, j][2]
                S = (a + b + c)
                a = S + depth * 2
                b = S + depth
                c = S
                if (a > 255):
                    a = 255
                if (b > 255):
                    b = 255
                if (c > 255):
                    c = 255
                draw.point((i, j), (a, b, c))
        return ImageQt(image.convert('RGBA'))

    def get_gray(self):
        image = self.__load_image()
        draw = ImageDraw.Draw(image)
        width = image.size[0]
        height = image.size[1]
        pix = image.load()

        for i in range(width):
            for j in range(height):
                a = pix[i, j][0]
                b = pix[i, j][1]
                c = pix[i, j][2]
                S = (a + b + c)
                draw.point((i, j), (S, S, S))
        return ImageQt(image.convert('RGBA'))

    def get_black_white(self):
        image = self.__load_image()
        draw = ImageDraw.Draw(image)
        width = image.size[0]
        height = image.size[1]
        pix = image.load()

        factor = 50
        for i in range(width):
            for j in range(height):
                a = pix[i, j][0]
                b = pix[i, j][1]
                c = pix[i, j][2]
                S = a + b + c
                if (S > (((255 + factor) // 2) * 3)):
                    a, b, c = 255, 255, 255
                else:
                    a, b, c = 0, 0, 0
                draw.point((i, j), (a, b, c))
        return ImageQt(image.convert('RGBA'))

    def get_negative(self):
        image = self.__load_image()
        draw = ImageDraw.Draw(image)
        width = image.size[0]
        height = image.size[1]
        pix = image.load()

        for i in range(width):
            for j in range(height):
                a = pix[i, j][0]
                b = pix[i, j][1]
                c = pix[i, j][2]
                draw.point((i, j), (255 - a, 255 - b, 255 - c))
        return ImageQt(image.convert('RGBA'))


class ImageFilterWidnow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = ImageFilterDialog()
        self.ui.setupUi(self)
        self.imageFilter = ImageFilter('', self.ui.sizeSbx.value())
        self.init_ui()

    def init_ui(self):

        def register_rbn_eff(rbn, eff):
            rbn.clicked.connect(lambda: self.update_image(self.effects[eff]()))

        self.effects = {
            'None': self.imageFilter.get_image,
            'Sepia': self.imageFilter.get_sepia,
            'Gray': self.imageFilter.get_gray,
            'Bw': self.imageFilter.get_black_white,
            'Negative': self.imageFilter.get_negative,
        }
        self.ui.openFileBtn.clicked.connect(self.open_file)
        self.ui.sizeSbx.valueChanged.connect(self.set_size)

        self.ui.imageLbl.mousePressEvent = self.lbl_mousePressEvent
        self.ui.imageLbl.mouseMoveEvent = self.lbl_mouseMoveEvent
        self.ui.imageLbl.mouseReleaseEvent = self.lbl_mouseReleaseEvent

        register_rbn_eff(self.ui.nonEffectRbn, 'None')
        register_rbn_eff(self.ui.sepiaEffectRbn, 'Sepia')
        register_rbn_eff(self.ui.grayEffectRbn, 'Gray')
        register_rbn_eff(self.ui.bwEffectRbn, 'Bw')
        register_rbn_eff(self.ui.negativeEffectRbn, 'Negative')

    def open_file(self):
        dialog = QFileDialog(self)
        path = dialog.getOpenFileName()[0]
        if not path:
            return
        self.imageFilter.imageFile = path
        self.ui.effectsGbx.setEnabled(True)
        self.ui.nonEffectRbn.setChecked(True)
        self.update_image(self.effects['None']())

    def save_file(self, filepath, size=None):
        pix = self.ui.imageLbl.pixmap()
        if size:
            pix = pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        pix.save(filepath, 'PNG')

    def set_size(self, s):
        self.imageFilter.size = s

    def update_image(self, img):
        pix = QPixmap.fromImage(img)
        size = self.imageFilter.size
        pix = pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ui.imageLbl.setPixmap(pix)

    def get_delta(self):
        lbl_size = self.ui.imageLbl.size()
        pix = self.ui.imageLbl.pixmap()
        if not pix:
            return QPoint(0, 0)
        size = (lbl_size - pix.size()) / 2
        return QPoint(size.width(), size.height())

    def lbl_mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            if hasattr(self, 'currentQRubberBand'):
                self.currentQRubberBand.hide()
                self.currentQRubberBand.deleteLater()
                del self.currentQRubberBand

        if event.button() != Qt.LeftButton:
            return
        self.originQPoint = event.pos()
        self.currentQRubberBand = QRubberBand(QRubberBand.Rectangle, self.ui.imageLbl)
        self.currentQRubberBand.setGeometry(QRect(self.originQPoint, QSize()))
        self.currentQRubberBand.show()

    def lbl_mouseMoveEvent(self, event):
        if hasattr(self, 'currentQRubberBand'):
            self.currentQRubberBand.setGeometry(QRect(self.originQPoint,
                                                  event.pos()).normalized())

    def lbl_mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton or not hasattr(self, 'currentQRubberBand'):
            return
        self.currentQRubberBand.hide()
        rect = self.currentQRubberBand.geometry()
        d = self.get_delta()
        rect = QRect(rect.x() - d.x(), rect.y() - d.y(),
                     rect.width(), rect.height())
        self.currentQRubberBand.deleteLater()
        pix = self.ui.imageLbl.pixmap()
        crop_pixmap = pix.copy(rect)
        self.ui.imageLbl.setPixmap(crop_pixmap)


class TestChatWindow(QDialog):

    PATTERN = ''
    USER = 'TestUser'
    SMILES_DIR = r'resources\smiles'

    def __init__(self, parent=None):
        super().__init__(parent)
        ui_file = os.path.join(os.path.dirname(__file__),'test_chat.ui')
        loadUi(ui_file, self)
        self.__init_ui()
        self.load_smiles()

    @property
    def message_widget(self):
        return self.messageTxa

    def __init_ui(self):
        self.sendMsgBtn.clicked.connect(self.send_message)
        self.smilesCbx.activated.connect(self.add_selected_smils)
        # self.message_widget.textChanged.connect(lambda: print(self.message_widget.toHtml()))

    def __add_message_in_chat(self, message):
        import random
        test_time = f'{random.randint(1,12)}:{random.randint(1,60)}'
        item = QListWidgetItem()
        widget = MessageWidget(self.USER, message, test_time)
        item.setSizeHint(widget.sizeHint())
        self.chatList.addItem(item)
        self.chatList.setItemWidget(item, widget)

    def send_message(self):
        text = self.message_widget.toPlainText()
        html = self.message_widget.toHtml()
        self.__add_message_in_chat(text)
        self.message_widget.clear()

    def load_smiles(self):
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', self.SMILES_DIR))
        for file in os.listdir(path):
            file = os.path.join(path, file)
            if not os.path.isfile(file):
                continue
            icon = QIcon(file)
            self.smilesCbx.addItem(icon, '', userData=file)
        pass

    def add_selected_smils(self):
        data = self.smilesCbx.currentData()
        cursor = self.message_widget.textCursor()
        cursor.insertHtml(f'<img src="{data}" width="25" height="25">')


def main():
    app = QApplication([])
    # win = ImageFilterWidnow()
    win = TestChatWindow()
    win.show()
    app.exec_()


if __name__ == '__main__':
    main()
