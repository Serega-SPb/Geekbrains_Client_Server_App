""" Module implements addinional widgets """

from PyQt5.QtCore import Qt
from PyQt5.Qt import QSizePolicy, QFrame, QAbstractScrollArea
from PyQt5.QtWidgets import QWidget, QDialog, \
                            QGridLayout, QHBoxLayout, \
                            QLabel, QPushButton, QTextBrowser

from .login_ui import Ui_Dialog as LoginDialog


class UserWidget(QWidget):
    """ Class the widget of list item to display user """

    def __init__(self, username, action_name, action, parent=None):
        super().__init__(parent)
        self.ui()
        self.userLbl.setText(username)
        self.username = username
        self.actinBtn.setText(action_name)
        self.actinBtn.clicked.connect(action)

    def ui(self):
        """ Method build ui """

        # self.resize(200, 50)
        box = QHBoxLayout(self)
        self.setLayout(box)

        self.userLbl = QLabel(self)
        self.actinBtn = QPushButton(self)
        self.actinBtn.setFixedSize(50, 25)

        box.addWidget(self.userLbl)
        box.addWidget(self.actinBtn)


class Message(QWidget):
    """ Class the widget of list item to display message in chat """

    def __init__(self, user, text, time, parent=None):
        super().__init__(parent)
        self.ui()

        self.userLbl.setText(user)
        self.timeLbl.setText(time)
        self.msgLbl.setHtml(text)

    def ui(self):
        """ Method build ui """
        grid = QGridLayout(self)
        self.setLayout(grid)

        self.userLbl = QLabel(self)
        self.timeLbl = QLabel(self)
        self.msgLbl = QTextBrowser(self)
        self.msgLbl.setFrameShape(QFrame.NoFrame)
        self.msgLbl.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.msgLbl.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        self.timeLbl.setAlignment(Qt.AlignRight)

        grid.addWidget(self.userLbl, 0, 0)
        grid.addWidget(self.timeLbl, 0, 1)
        grid.addWidget(self.msgLbl, 1, 0, 1, 2)


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


def main():
    pass


if __name__ == '__main__':
    main()
