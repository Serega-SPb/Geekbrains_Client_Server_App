from PyQt5.QtWidgets import QApplication

from ui.additional_ui import TestChatWindow


def main():
    app = QApplication([])
    win = TestChatWindow()
    win.show()
    app.exec_()


if __name__ == '__main__':
    main()
