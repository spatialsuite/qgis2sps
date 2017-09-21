# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qgis2sps_dialog_base.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_qgis2spsDialogBase(object):
    def setupUi(self, qgis2spsDialogBase):
        qgis2spsDialogBase.setObjectName(_fromUtf8("qgis2spsDialogBase"))
        qgis2spsDialogBase.resize(573, 385)
        self.label = QtGui.QLabel(qgis2spsDialogBase)
        self.label.setGeometry(QtCore.QRect(30, 20, 101, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(qgis2spsDialogBase)
        self.label_2.setGeometry(QtCore.QRect(320, 20, 71, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(qgis2spsDialogBase)
        self.label_3.setGeometry(QtCore.QRect(320, 90, 101, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.targets = QtGui.QCheckBox(qgis2spsDialogBase)
        self.targets.setGeometry(QtCore.QRect(320, 160, 101, 17))
        self.targets.setChecked(True)
        self.targets.setObjectName(_fromUtf8("targets"))
        self.presentations = QtGui.QCheckBox(qgis2spsDialogBase)
        self.presentations.setGeometry(QtCore.QRect(420, 160, 131, 17))
        self.presentations.setChecked(True)
        self.presentations.setObjectName(_fromUtf8("presentations"))
        self.includes = QtGui.QCheckBox(qgis2spsDialogBase)
        self.includes.setGeometry(QtCore.QRect(320, 190, 101, 17))
        self.includes.setChecked(True)
        self.includes.setObjectName(_fromUtf8("includes"))
        self.label_4 = QtGui.QLabel(qgis2spsDialogBase)
        self.label_4.setGeometry(QtCore.QRect(30, 340, 131, 16))
        font = QtGui.QFont()
        font.setItalic(True)
        font.setUnderline(True)
        self.label_4.setFont(font)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_5 = QtGui.QLabel(qgis2spsDialogBase)
        self.label_5.setGeometry(QtCore.QRect(320, 220, 71, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.listWidget = QtGui.QListWidget(qgis2spsDialogBase)
        self.listWidget.setGeometry(QtCore.QRect(30, 50, 241, 261))
        self.listWidget.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.lineEdit = QtGui.QLineEdit(qgis2spsDialogBase)
        self.lineEdit.setGeometry(QtCore.QRect(320, 110, 191, 31))
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.pushButton = QtGui.QPushButton(qgis2spsDialogBase)
        self.pushButton.setGeometry(QtCore.QRect(520, 110, 31, 31))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.lineEdit_2 = QtGui.QLineEdit(qgis2spsDialogBase)
        self.lineEdit_2.setGeometry(QtCore.QRect(320, 40, 191, 31))
        self.lineEdit_2.setObjectName(_fromUtf8("lineEdit_2"))
        self.textEdit = QtGui.QTextEdit(qgis2spsDialogBase)
        self.textEdit.setGeometry(QtCore.QRect(320, 240, 231, 71))
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.pushButton_2 = QtGui.QPushButton(qgis2spsDialogBase)
        self.pushButton_2.setGeometry(QtCore.QRect(370, 340, 85, 27))
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.pushButton_3 = QtGui.QPushButton(qgis2spsDialogBase)
        self.pushButton_3.setGeometry(QtCore.QRect(470, 340, 85, 27))
        self.pushButton_3.setObjectName(_fromUtf8("pushButton_3"))

        self.retranslateUi(qgis2spsDialogBase)
        QtCore.QMetaObject.connectSlotsByName(qgis2spsDialogBase)

    def retranslateUi(self, qgis2spsDialogBase):
        qgis2spsDialogBase.setWindowTitle(_translate("qgis2spsDialogBase", "Sweco : Qgis2Sps", None))
        self.label.setText(_translate("qgis2spsDialogBase", "Tilgængelige lag", None))
        self.label_2.setText(_translate("qgis2spsDialogBase", "Modulnavn", None))
        self.label_3.setText(_translate("qgis2spsDialogBase", "Modulmappe", None))
        self.targets.setText(_translate("qgis2spsDialogBase", "Targetset", None))
        self.presentations.setText(_translate("qgis2spsDialogBase", "Presentations", None))
        self.includes.setText(_translate("qgis2spsDialogBase", "Includes", None))
        self.label_4.setText(_translate("qgis2spsDialogBase", "Sweco 2017 - Version 1", None))
        self.label_5.setText(_translate("qgis2spsDialogBase", "Status", None))
        self.pushButton.setText(_translate("qgis2spsDialogBase", "...", None))
        self.pushButton_2.setText(_translate("qgis2spsDialogBase", "Dan Modul", None))
        self.pushButton_3.setText(_translate("qgis2spsDialogBase", "Luk", None))

