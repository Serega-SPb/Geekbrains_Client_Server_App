from PyQt5.QtWidgets import QApplication

from ui.additional_ui import ImageFilterWidnow


def main():
    app = QApplication([])
    win = ImageFilterWidnow()
    win.show()
    app.exec_()


if __name__ == '__main__':
    main()
