import os
import sys

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QPlainTextEdit

from client_crypt import ClientCrypt


class EncryptorMainWindwo(QMainWindow):

    encryptors = {}

    def __init__(self, parent=None):
        super().__init__(parent)
        ui_file = os.path.join(os.path.dirname(__file__), 'encryptor.ui')
        loadUi(ui_file, self)
        self.__init_ui()

    def __init_ui(self):
        self.encryptBtn.clicked.connect(self.encrypt)
        self.decryptBtn.clicked.connect(self.decrypt)

    @property
    def input_encr_pte(self):
        return self.inputEncryptPte

    @property
    def output_encr_pte(self):
        return self.outputEncryptPte

    @property
    def input_decr_pte(self):
        return self.inputDecryptPte

    @property
    def output_decr_pte(self):
        return self.outputDecryptPte

    @property
    def secret(self):
        return self.secretLE

    def get_encryptor(self) -> ClientCrypt:
        secret = self.padding_secret()
        if secret not in self.encryptors.keys():
            self.encryptors[secret] = ClientCrypt(secret)
        return self.encryptors[secret]

    def show_message_box(self, title, text):
        QMessageBox.information(self, title, text)

    def padding_secret(self):
        text = self.secret.text().encode()
        return text + b" " * (16 - len(text) % 16)

    def encrypt(self):
        if not self.secret.text():
            self.show_message_box('Warning', 'Secret is empty')
            return
        if not self.input_encr_pte.toPlainText():
            self.show_message_box('Warning', 'Encrypt text is empty')
            return

        try:
            text = self.input_encr_pte.toPlainText().encode()
            encryptor = self.get_encryptor()
            encr_text = encryptor.encript_msg(text).decode()
            self.output_encr_pte.setPlainText(encr_text)
        except Exception as e:
            self.show_message_box('Error', str(e))

    def decrypt(self):
        if not self.secret.text():
            self.show_message_box('Warning', 'Secret is empty')
            return
        if not self.input_decr_pte.toPlainText():
            self.show_message_box('Warning', 'Decrypt text is empty')
            return

        try:
            text = self.input_decr_pte.toPlainText().encode()
            encryptor = self.get_encryptor()
            decr_text = encryptor.decrypt_msg(text).decode()
            self.output_decr_pte.setPlainText(decr_text)
        except Exception as e:
            self.show_message_box('Error', str(e))


def main():
    app = QApplication(sys.argv)
    win = EncryptorMainWindwo()
    win.show()
    app.exec_()


if __name__ == '__main__':
    main()
