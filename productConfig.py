# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\productConfig.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_productDialog(object):
    def setupUi(self, productDialog):
        productDialog.setObjectName("productDialog")
        productDialog.resize(344, 241)
        productDialog.setWhatsThis("")
        self.Table = QtWidgets.QTableWidget(productDialog)
        self.Table.setGeometry(QtCore.QRect(0, 10, 341, 191))
        self.Table.setAcceptDrops(False)
        self.Table.setObjectName("Table")
        self.Table.setColumnCount(3)
        self.Table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(9)
        item.setFont(font)
        self.Table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(9)
        item.setFont(font)
        self.Table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.Table.setHorizontalHeaderItem(2, item)
        self.saveBtn = QtWidgets.QPushButton(productDialog)
        self.saveBtn.setGeometry(QtCore.QRect(220, 210, 71, 23))
        self.saveBtn.setWhatsThis("")
        self.saveBtn.setObjectName("saveBtn")
        self.insertBtn = QtWidgets.QPushButton(productDialog)
        self.insertBtn.setGeometry(QtCore.QRect(60, 210, 71, 23))
        self.insertBtn.setObjectName("insertBtn")
        self.importBtn = QtWidgets.QPushButton(productDialog)
        self.importBtn.setGeometry(QtCore.QRect(140, 210, 71, 23))
        self.importBtn.setObjectName("importBtn")

        self.retranslateUi(productDialog)
        QtCore.QMetaObject.connectSlotsByName(productDialog)

    def retranslateUi(self, productDialog):
        _translate = QtCore.QCoreApplication.translate
        productDialog.setWindowTitle(_translate("productDialog", "Dialog"))
        item = self.Table.horizontalHeaderItem(0)
        item.setText(_translate("productDialog", "部门"))
        item = self.Table.horizontalHeaderItem(1)
        item.setText(_translate("productDialog", "关键字"))
        item = self.Table.horizontalHeaderItem(2)
        item.setText(_translate("productDialog", "操作"))
        self.saveBtn.setText(_translate("productDialog", "保存"))
        self.insertBtn.setText(_translate("productDialog", "添加"))
        self.importBtn.setText(_translate("productDialog", "导入"))
