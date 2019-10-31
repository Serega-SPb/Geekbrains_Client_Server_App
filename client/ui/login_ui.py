# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Repositories\Geekbrains_Client_Server_App\client\ui\login.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(320, 120)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(320, 120))
        Dialog.setMaximumSize(QtCore.QSize(320, 120))
        font = QtGui.QFont()
        font.setPointSize(10)
        Dialog.setFont(font)
        Dialog.setModal(True)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.usernameTxb = QtWidgets.QLineEdit(Dialog)
        self.usernameTxb.setObjectName("usernameTxb")
        self.gridLayout.addWidget(self.usernameTxb, 1, 1, 1, 1)
        self.passwordTxb = QtWidgets.QLineEdit(Dialog)
        self.passwordTxb.setEchoMode(QtWidgets.QLineEdit.Password)
        self.passwordTxb.setObjectName("passwordTxb")
        self.gridLayout.addWidget(self.passwordTxb, 2, 1, 1, 1)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(50, -1, 50, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.loginBtn = QtWidgets.QPushButton(Dialog)
        self.loginBtn.setObjectName("loginBtn")
        self.horizontalLayout.addWidget(self.loginBtn)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.exitBtn = QtWidgets.QPushButton(Dialog)
        self.exitBtn.setObjectName("exitBtn")
        self.horizontalLayout.addWidget(self.exitBtn)
        self.gridLayout.addLayout(self.horizontalLayout, 3, 0, 1, 2)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        self.ipAddressTxb = QtWidgets.QLineEdit(Dialog)
        self.ipAddressTxb.setObjectName("ipAddressTxb")
        self.horizontalLayout_2.addWidget(self.ipAddressTxb)
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_2.addWidget(self.label_4)
        self.portTxb = QtWidgets.QLineEdit(Dialog)
        self.portTxb.setMaximumSize(QtCore.QSize(50, 16777215))
        self.portTxb.setObjectName("portTxb")
        self.horizontalLayout_2.addWidget(self.portTxb)
        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.loginBtn, self.exitBtn)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Login"))
        self.label.setText(_translate("Dialog", "Username"))
        self.loginBtn.setText(_translate("Dialog", "Login"))
        self.exitBtn.setText(_translate("Dialog", "Exit"))
        self.label_2.setText(_translate("Dialog", "Password"))
        self.label_3.setText(_translate("Dialog", "Connect to"))
        self.label_4.setText(_translate("Dialog", ":"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
