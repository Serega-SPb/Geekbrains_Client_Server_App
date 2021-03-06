# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Repositories\Geekbrains_Client_Server_App\client\ui\client.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setMinimumSize(QtCore.QSize(600, 500))
        font = QtGui.QFont()
        font.setPointSize(10)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.gridLayout.setObjectName("gridLayout")
        self.contactsGridLayout = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.contactsGridLayout.sizePolicy().hasHeightForWidth())
        self.contactsGridLayout.setSizePolicy(sizePolicy)
        self.contactsGridLayout.setObjectName("contactsGridLayout")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.contactsGridLayout)
        self.gridLayout_3.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.tabWidget = QtWidgets.QTabWidget(self.contactsGridLayout)
        self.tabWidget.setMinimumSize(QtCore.QSize(250, 0))
        self.tabWidget.setObjectName("tabWidget")
        self.usersTab = QtWidgets.QWidget()
        self.usersTab.setObjectName("usersTab")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.usersTab)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.addContactTbx = QtWidgets.QLineEdit(self.usersTab)
        self.addContactTbx.setObjectName("addContactTbx")
        self.horizontalLayout_3.addWidget(self.addContactTbx)
        self.addContactBtn = QtWidgets.QPushButton(self.usersTab)
        self.addContactBtn.setEnabled(False)
        self.addContactBtn.setObjectName("addContactBtn")
        self.horizontalLayout_3.addWidget(self.addContactBtn)
        self.gridLayout_4.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)
        self.usersList = QtWidgets.QListWidget(self.usersTab)
        self.usersList.setFrameShape(QtWidgets.QFrame.Box)
        self.usersList.setObjectName("usersList")
        self.gridLayout_4.addWidget(self.usersList, 2, 0, 1, 1)
        self.tabWidget.addTab(self.usersTab, "")
        self.contactsTab = QtWidgets.QWidget()
        self.contactsTab.setObjectName("contactsTab")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.contactsTab)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.contactsList = QtWidgets.QListWidget(self.contactsTab)
        self.contactsList.setObjectName("contactsList")
        self.gridLayout_5.addWidget(self.contactsList, 0, 0, 1, 1)
        self.tabWidget.addTab(self.contactsTab, "")
        self.gridLayout_3.addWidget(self.tabWidget, 1, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.avatarLbl = QtWidgets.QLabel(self.contactsGridLayout)
        self.avatarLbl.setMinimumSize(QtCore.QSize(50, 50))
        self.avatarLbl.setMaximumSize(QtCore.QSize(50, 50))
        self.avatarLbl.setFrameShape(QtWidgets.QFrame.Box)
        self.avatarLbl.setText("")
        self.avatarLbl.setObjectName("avatarLbl")
        self.horizontalLayout.addWidget(self.avatarLbl)
        self.usernameLbl = QtWidgets.QLabel(self.contactsGridLayout)
        self.usernameLbl.setObjectName("usernameLbl")
        self.horizontalLayout.addWidget(self.usernameLbl)
        self.gridLayout_3.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.contactsGridLayout, 0, 0, 2, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setContentsMargins(-1, -1, 15, -1)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.messageTxa = QtWidgets.QTextEdit(self.centralwidget)
        self.messageTxa.setMaximumSize(QtCore.QSize(16777215, 50))
        self.messageTxa.setObjectName("messageTxa")
        self.gridLayout_2.addWidget(self.messageTxa, 4, 0, 1, 1)
        self.chatList = QtWidgets.QListWidget(self.centralwidget)
        self.chatList.setEnabled(True)
        self.chatList.setLineWidth(1)
        self.chatList.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.chatList.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.chatList.setObjectName("chatList")
        self.gridLayout_2.addWidget(self.chatList, 1, 0, 2, 4)
        self.sendMsgBtn = QtWidgets.QPushButton(self.centralwidget)
        self.sendMsgBtn.setMinimumSize(QtCore.QSize(0, 50))
        self.sendMsgBtn.setObjectName("sendMsgBtn")
        self.gridLayout_2.addWidget(self.sendMsgBtn, 4, 1, 1, 3)
        self.gridLayout.addLayout(self.gridLayout_2, 1, 1, 1, 4)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, -1, 15, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.chatNameLbl = QtWidgets.QLabel(self.centralwidget)
        self.chatNameLbl.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chatNameLbl.sizePolicy().hasHeightForWidth())
        self.chatNameLbl.setSizePolicy(sizePolicy)
        self.chatNameLbl.setObjectName("chatNameLbl")
        self.horizontalLayout_2.addWidget(self.chatNameLbl)
        self.closeChatBtn = QtWidgets.QPushButton(self.centralwidget)
        self.closeChatBtn.setMinimumSize(QtCore.QSize(25, 25))
        self.closeChatBtn.setMaximumSize(QtCore.QSize(25, 25))
        self.closeChatBtn.setObjectName("closeChatBtn")
        self.horizontalLayout_2.addWidget(self.closeChatBtn)
        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 1, 1, 4)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.addContactBtn.setText(_translate("MainWindow", "Add"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.usersTab), _translate("MainWindow", "Users"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.contactsTab), _translate("MainWindow", "Contacts"))
        self.usernameLbl.setText(_translate("MainWindow", "USER"))
        self.sendMsgBtn.setText(_translate("MainWindow", "Send"))
        self.chatNameLbl.setText(_translate("MainWindow", "CHAT_NAME"))
        self.closeChatBtn.setText(_translate("MainWindow", "X"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
