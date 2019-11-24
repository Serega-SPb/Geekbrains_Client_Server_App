# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Repositories\Geekbrains_Client_Server_App\les_20_hw\test.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.dbTabControl = QtWidgets.QTabWidget(self.centralwidget)
        self.dbTabControl.setObjectName("dbTabControl")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.dbTabControl.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.dbTabControl.addTab(self.tab_2, "")
        self.gridLayout.addWidget(self.dbTabControl, 0, 0, 1, 3)
        self.inputTbx = QtWidgets.QLineEdit(self.centralwidget)
        self.inputTbx.setObjectName("inputTbx")
        self.gridLayout.addWidget(self.inputTbx, 1, 0, 1, 1)
        self.addBtn = QtWidgets.QPushButton(self.centralwidget)
        self.addBtn.setObjectName("addBtn")
        self.gridLayout.addWidget(self.addBtn, 1, 1, 1, 1)
        self.searchBtn = QtWidgets.QPushButton(self.centralwidget)
        self.searchBtn.setObjectName("searchBtn")
        self.gridLayout.addWidget(self.searchBtn, 1, 2, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.dbTabControl.setTabText(self.dbTabControl.indexOf(self.tab), _translate("MainWindow", "Tab 1"))
        self.dbTabControl.setTabText(self.dbTabControl.indexOf(self.tab_2), _translate("MainWindow", "Tab 2"))
        self.addBtn.setText(_translate("MainWindow", "add"))
        self.searchBtn.setText(_translate("MainWindow", "search"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
