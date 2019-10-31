# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Repositories\Geekbrains_Client_Server_App\server\ui\server_config.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(409, 150)
        Dialog.setMinimumSize(QtCore.QSize(400, 150))
        Dialog.setMaximumSize(QtCore.QSize(409, 200))
        font = QtGui.QFont()
        font.setPointSize(8)
        Dialog.setFont(font)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.db_filepath_txb = QtWidgets.QLineEdit(Dialog)
        self.db_filepath_txb.setObjectName("db_filepath_txb")
        self.gridLayout.addWidget(self.db_filepath_txb, 0, 1, 1, 1)
        self.select_file_btn = QtWidgets.QToolButton(Dialog)
        self.select_file_btn.setObjectName("select_file_btn")
        self.gridLayout.addWidget(self.select_file_btn, 0, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.port_txb = QtWidgets.QLineEdit(Dialog)
        self.port_txb.setObjectName("port_txb")
        self.gridLayout.addWidget(self.port_txb, 1, 1, 1, 2)
        self.label_3 = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.bind_addr_txb = QtWidgets.QLineEdit(Dialog)
        self.bind_addr_txb.setObjectName("bind_addr_txb")
        self.gridLayout.addWidget(self.bind_addr_txb, 2, 1, 1, 2)
        spacerItem = QtWidgets.QSpacerItem(388, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 3)
        self.btns_h_layout = QtWidgets.QHBoxLayout()
        self.btns_h_layout.setObjectName("btns_h_layout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.btns_h_layout.addItem(spacerItem1)
        self.save_btn = QtWidgets.QPushButton(Dialog)
        self.save_btn.setObjectName("save_btn")
        self.btns_h_layout.addWidget(self.save_btn)
        self.cancel_btn = QtWidgets.QPushButton(Dialog)
        self.cancel_btn.setObjectName("cancel_btn")
        self.btns_h_layout.addWidget(self.cancel_btn)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.btns_h_layout.addItem(spacerItem2)
        self.gridLayout.addLayout(self.btns_h_layout, 4, 0, 1, 3)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Config"))
        self.label.setText(_translate("Dialog", "Database file"))
        self.select_file_btn.setText(_translate("Dialog", "..."))
        self.label_2.setText(_translate("Dialog", "Port"))
        self.label_3.setText(_translate("Dialog", "Bind address"))
        self.save_btn.setText(_translate("Dialog", "Save"))
        self.cancel_btn.setText(_translate("Dialog", "Cancel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
