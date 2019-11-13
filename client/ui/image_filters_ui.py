# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Repositories\Geekbrains_Client_Server_App\client\ui\image_filters.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(800, 600)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.openFileBtn = QtWidgets.QPushButton(Dialog)
        self.openFileBtn.setMaximumSize(QtCore.QSize(150, 25))
        self.openFileBtn.setObjectName("openFileBtn")
        self.gridLayout.addWidget(self.openFileBtn, 0, 0, 1, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.imageLbl = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imageLbl.sizePolicy().hasHeightForWidth())
        self.imageLbl.setSizePolicy(sizePolicy)
        self.imageLbl.setText("")
        self.imageLbl.setScaledContents(False)
        self.imageLbl.setAlignment(QtCore.Qt.AlignCenter)
        self.imageLbl.setObjectName("imageLbl")
        self.gridLayout_2.addWidget(self.imageLbl, 0, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 2, 0, 1, 2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.sizeSbx = QtWidgets.QSpinBox(Dialog)
        self.sizeSbx.setMinimum(64)
        self.sizeSbx.setMaximum(1024)
        self.sizeSbx.setStepType(QtWidgets.QAbstractSpinBox.DefaultStepType)
        self.sizeSbx.setProperty("value", 512)
        self.sizeSbx.setObjectName("sizeSbx")
        self.horizontalLayout.addWidget(self.sizeSbx)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.effectsGbx = QtWidgets.QGroupBox(Dialog)
        self.effectsGbx.setEnabled(False)
        self.effectsGbx.setMaximumSize(QtCore.QSize(16777215, 50))
        self.effectsGbx.setAlignment(QtCore.Qt.AlignCenter)
        self.effectsGbx.setObjectName("effectsGbx")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.effectsGbx)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.nonEffectRbn = QtWidgets.QRadioButton(self.effectsGbx)
        self.nonEffectRbn.setChecked(True)
        self.nonEffectRbn.setObjectName("nonEffectRbn")
        self.horizontalLayout_2.addWidget(self.nonEffectRbn)
        self.sepiaEffectRbn = QtWidgets.QRadioButton(self.effectsGbx)
        self.sepiaEffectRbn.setObjectName("sepiaEffectRbn")
        self.horizontalLayout_2.addWidget(self.sepiaEffectRbn)
        self.grayEffectRbn = QtWidgets.QRadioButton(self.effectsGbx)
        self.grayEffectRbn.setObjectName("grayEffectRbn")
        self.horizontalLayout_2.addWidget(self.grayEffectRbn)
        self.bwEffectRbn = QtWidgets.QRadioButton(self.effectsGbx)
        self.bwEffectRbn.setObjectName("bwEffectRbn")
        self.horizontalLayout_2.addWidget(self.bwEffectRbn)
        self.negativeEffectRbn = QtWidgets.QRadioButton(self.effectsGbx)
        self.negativeEffectRbn.setObjectName("negativeEffectRbn")
        self.horizontalLayout_2.addWidget(self.negativeEffectRbn)
        self.gridLayout.addWidget(self.effectsGbx, 0, 1, 2, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.openFileBtn.setText(_translate("Dialog", "Open image"))
        self.label.setText(_translate("Dialog", "Size"))
        self.effectsGbx.setTitle(_translate("Dialog", "Effects"))
        self.nonEffectRbn.setText(_translate("Dialog", "None"))
        self.sepiaEffectRbn.setText(_translate("Dialog", "Sepia"))
        self.grayEffectRbn.setText(_translate("Dialog", "Gray"))
        self.bwEffectRbn.setText(_translate("Dialog", "BW"))
        self.negativeEffectRbn.setText(_translate("Dialog", "Negative"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
