# This is a sample Python script.
import base64
import datetime
import functools
import os.path
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import sys
import time

import yaml
from PyQt5.QtWidgets import *
import shutil

from my import *
import logging
import pandas as pd
from productConfig import Ui_productDialog

Logger = logging.getLogger("test_log")
Logger.setLevel(logging.INFO)
fh = logging.FileHandler("test.log")
fmt = "\n[%(asctime)s-%(name)s-%(levelname)s]: %(message)s"
formatter = logging.Formatter(fmt)
fh.setFormatter(formatter)
Logger.addHandler(fh)

ProductFile = 'productConf.yml'
OtherFile = 'otherConf.yml'


def get_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log_exception(fn):
    @functools.wraps(fn)
    def wrapper(self):
        try:
            fn(self)
        except Exception as e:
            Logger.exception("[Error in {}] msg: {}".format(__name__, str(e)))
            raise

    return wrapper


class ConfDialog(QDialog, Ui_productDialog):
    def __init__(self, title: str, conf_file: str, parent=None):
        super(ConfDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(title)
        self.setFixedSize(345, 242)
        self.initPath = 'c:\\'
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap('static/title.ico'))
        self.setWindowIcon(icon)
        self.file = conf_file
        self.insertBtn.clicked.connect(self.insert_item)
        self.saveBtn.clicked.connect(self.save_conf)
        self.importBtn.clicked.connect(self.import_conf)
        self.Table.setHorizontalHeaderLabels(['部门', '关键字', '操作'])
        if os.path.exists(self.file):
            with open(self.file, encoding='utf-8') as f:
                self.confData = yaml.safe_load(f)['conf']
        else:
            self.confData = []
        self.row = 0
        self.update_table()

    def insert_item(self):
        self.save_table()
        self.confData.append(['', ''])
        self.update_table()

    def update_table(self):
        self.row = len(self.confData)
        self.Table.setRowCount(self.row)
        self.Table.setColumnCount(3)
        for i in range(self.row):
            for j in range(2):
                self.Table.setItem(i, j, QTableWidgetItem(str(self.confData[i][j])))
            self.Table.setCellWidget(i, 2, self.delete_btn(i))

    def import_conf(self):
        FDialog = QFileDialog(self)
        FDialog.setFileMode(QFileDialog.ExistingFile)
        FDialog.setDirectory(self.initPath)
        FDialog.setNameFilter('文件(*.csv *.xlsx *.xls)')
        if FDialog.exec_():
            file = FDialog.selectedFiles()[0]
            fileType = str(file).split('.')[-1]
            self.initPath = os.path.dirname(file)
            try:
                data = pd.read_csv(file, encoding='gb2312') if fileType == 'csv' else pd.read_excel(file)
                data.to_dict()
            except Exception:
                QMessageBox.warning(self.Table, '文件检查', '检查数据，按模板数据导入', QMessageBox.Ok)
                return
            headers = ['部门', '关键字']
            if headers != data.keys().tolist():
                QMessageBox.warning(self.Table, '文件检查', '检查数据，按模板数据导入', QMessageBox.Ok)
                return
            else:
                self.confData = data[headers].values.tolist()
                self.update_table()

    def delete_btn(self, index):
        Btn = QtWidgets.QPushButton('删除')
        Btn.setFlat(True)
        Btn.clicked.connect(lambda: self.delete_row(index))
        return Btn

    def save_conf(self):
        self.save_table()
        save_data = {'conf': []}
        flag = True
        for i in range(len(self.confData)):
            dept, key = self.confData[i][0].strip(), self.confData[i][1].strip()
            if not dept:
                QMessageBox.warning(self.Table, '文件检查', f'第{i + 1}行部门不能为空', QMessageBox.Ok)
                flag = False
                break
            elif not key:
                flag = False
                QMessageBox.warning(self.Table, '关键字检查', f'第{i + 1}行关键字不能为空', QMessageBox.Ok)
                break
            else:
                save_data['conf'].append([dept, key])
        with open(self.file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(save_data, f, allow_unicode=True)
        if flag:
            self.close()

    def delete_row(self, index):
        self.save_table()
        del self.confData[index]
        self.update_table()

    def save_table(self):
        self.confData = []
        for i in range(self.Table.rowCount()):
            self.confData.append([self.Table.item(i, j).text() for j in range(2)])


class ConfSet:

    def __init__(self):
        self.otherData = {}  # 其他资料识别关键字
        self.productData = {}  # 产品识别关键字

    @property
    def other_key_list(self):
        return [i for i in self.otherData]

    @property
    def product_key_list(self):
        return [i for i in self.productData]


class NameDir:

    def __init__(self):
        self.index = 0
        self.dirs = []  # 存储的文件目录

    @property
    def DirList(self):
        return self.dirs

    @property
    def Index(self):
        return self.index

    def index_add_one(self):
        self.index += 1

    def setDirs(self, dirs: list):
        self.dirs = dirs


class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.initInputOneProductPath = 'c:\\'
        self.initInputTwoProductPath = 'c:\\'
        self.initInputOneOtherPath = 'c:\\'
        self.initInputTwoOtherPath = 'c:\\'
        self.initInputHandoutPath = 'c:\\'
        self.ID = 'MTcxMTkwMDgwMC4w'
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap('static/title.ico'))
        self.setWindowIcon(icon)
        self.setFixedSize(487, 685)
        self.setObjectName('MainWindow')
        self.setupUi(self)
        self.inputOneProductFiles = []
        self.inputTwoProductFiles = []
        self.inputHandoutFiles = []
        self.inputProductFiles = []
        self.inputOneOtherFiles = []
        self.inputTwoOtherFiles = []
        self.outputPath = ''
        self.confSet = ConfSet()
        self.fileNameToDirDict = {}
        # 设置控件属性
        self.inputHandoutPath.setText('共选择0个文件')
        self.inputOneProductPath.setText('共选择0个文件')
        self.inputTwoProductPath.setText('共选择0个文件')
        self.inputOneOtherPath.setText('共选择0个文件')
        self.inputTwoOtherPath.setText('共选择0个文件')
        self.inputOneProductPath.setReadOnly(True)
        self.inputTwoProductPath.setReadOnly(True)
        self.inputOneOtherPath.setReadOnly(True)
        self.inputTwoOtherPath.setReadOnly(True)
        self.inputHandoutPath.setReadOnly(True)
        self.outputPathText.setReadOnly(True)
        self.logView.setReadOnly(True)
        # 清空文件
        self.clearHandoutBtn.clicked.connect(self.clear_hand_Out_files)
        self.clearOneProductBtn.clicked.connect(self.clear_one_product_files)
        self.clearTowProductBtn.clicked.connect(self.clear_two_product_files)
        self.clearOneOtherBtn.clicked.connect(self.clear_one_other_files)
        self.clearTwoOtherBtn.clicked.connect(self.clear_two_other_files)
        # 选择文件
        self.selectOneProductBtn.clicked.connect(self.choose_one_product_path)
        self.selectTwoProductBtn.clicked.connect(self.choose_two_product_path)
        self.selectOneOtherBtn.clicked.connect(self.choose_one_other_path)
        self.selectTwoOtherBtn.clicked.connect(self.choose_tow_other_path)
        self.selectHandoutBtn.clicked.connect(self.choose_handout_path)
        self.outputClick.clicked.connect(self.choose_output_path)

        # 配置按钮
        self.productConfButton.clicked.connect(lambda: self.open_conf(title='图纸配置', conf_file=ProductFile))
        self.otherConfButton.clicked.connect(lambda: self.open_conf(title='资料配置', conf_file=OtherFile))
        self.confFileName = 'config.yml'
        self.failNum = self.successNum = self.totalNum = 0
        self.savePath = ''

        # 运行按钮
        self.runButton.clicked.connect(self.start_run)
        self.runHandoutButton.clicked.connect(self.start_hand_out)
        self.runReadPicButton.clicked.connect(self.start_read_pic)

        # 初始化参数
        if os.path.exists(self.confFileName):
            with open('config.yml', encoding='utf-8') as f:
                params = yaml.safe_load(f)
                if '输出路径' in params and params['输出路径']:
                    self.outputPathText.setText(params['输出路径'])
                    self.outputPath = params['输出路径']

    def init_run(self):
        self.fileNameToDirDict = {}
        self.logView.clear()

    def choose_handout_path(self):
        FDialog = QFileDialog(self)
        FDialog.setFileMode(QFileDialog.ExistingFiles)
        FDialog.setDirectory(self.initInputHandoutPath)
        FDialog.setNameFilter('图片文件(*.jpg *.png *.jpeg *.tiff *.tif *.pdf *.bmp)')
        if FDialog.exec_():
            self.inputHandoutFiles = FDialog.selectedFiles()
            self.inputHandoutPath.setText(f'共选择{len(self.inputHandoutFiles)}个文件')
            self.initInputHandoutPath = os.path.dirname(self.inputHandoutFiles[0])

    def choose_one_product_path(self):
        FDialog = QFileDialog(self)
        FDialog.setFileMode(QFileDialog.ExistingFiles)
        FDialog.setDirectory(self.initInputOneProductPath)
        FDialog.setNameFilter('图片文件(*.jpg *.png *.jpeg *.tiff *.tif *.pdf *.bmp)')
        if FDialog.exec_():
            self.inputOneProductFiles = FDialog.selectedFiles()
            self.inputOneProductPath.setText(f'共选择{len(self.inputOneProductFiles)}个文件')
            self.initInputOneProductPath = os.path.dirname(self.inputOneProductFiles[0])

    def choose_two_product_path(self):
        FDialog = QFileDialog(self)
        FDialog.setFileMode(QFileDialog.ExistingFiles)
        FDialog.setDirectory(self.initInputTwoProductPath)
        FDialog.setNameFilter('图片文件(*.jpg *.png *.jpeg *.tiff *.tif *.pdf *.bmp)')
        if FDialog.exec_():
            self.inputTwoProductFiles = FDialog.selectedFiles()
            self.inputTwoProductPath.setText(f'共选择{len(self.inputTwoProductFiles)}个文件')
            self.initInputTwoProductPath = os.path.dirname(self.inputTwoProductFiles[0])

    def choose_one_other_path(self):
        FDialog = QFileDialog(self)
        FDialog.setFileMode(QFileDialog.ExistingFiles)
        FDialog.setDirectory(self.initInputOneOtherPath)
        FDialog.setNameFilter('图片文件(*.jpg *.png *.jpeg *.tiff *.tif *.pdf *.bmp)')
        if FDialog.exec_():
            self.inputOneOtherFiles = FDialog.selectedFiles()
            self.inputOneOtherPath.setText(f'共选择{len(self.inputOneOtherFiles)}个文件')
            self.initInputOneOtherPath = os.path.dirname(self.inputOneOtherFiles[0])

    def choose_tow_other_path(self):
        FDialog = QFileDialog(self)
        FDialog.setFileMode(QFileDialog.ExistingFiles)
        FDialog.setDirectory(self.initInputTwoOtherPath)
        FDialog.setNameFilter('图片文件(*.jpg *.png *.jpeg *.tiff *.tif *.pdf *.bmp)')
        if FDialog.exec_():
            self.inputTwoOtherFiles = FDialog.selectedFiles()
            self.inputTwoOtherPath.setText(f'共选择{len(self.inputTwoOtherFiles)}个文件')
            self.initInputTwoOtherPath = os.path.dirname(self.inputTwoOtherFiles[0])

    def clear_one_product_files(self):
        self.inputOneProductFiles = []
        self.inputOneProductPath.setText('共选择0个文件')

    def clear_two_product_files(self):
        self.inputTwoProductFiles = []
        self.inputTwoProductPath.setText('共选择0个文件')

    def clear_hand_Out_files(self):
        self.inputHandoutFiles = []
        self.inputHandoutPath.setText('共选择0个文件')

    def clear_one_other_files(self):
        self.inputOneOtherFiles = []
        self.inputOneOtherPath.setText('共选择0个文件')

    def clear_two_other_files(self):
        self.inputTwoOtherFiles = []
        self.inputTwoOtherPath.setText('共选择0个文件')

    @staticmethod
    def open_conf(title: str, conf_file: str):
        Dialog = ConfDialog(title=title, conf_file=conf_file)
        Dialog.exec()

    def choose_output_path(self):
        FDialog = QFileDialog(self)
        FDialog.setFileMode(QFileDialog.DirectoryOnly)
        FDialog.setDirectory(self.outputPath)
        if FDialog.exec_():
            self.outputPath = FDialog.selectedFiles()[0]
            self.outputPathText.setText(self.outputPath)

    def check_table(self):
        if self.tableRadio.isChecked():
            self.rowBox.setEnabled(True)

    def check_product(self):
        if self.productRadio.isChecked():
            self.rowBox.setEnabled(False)

    def read_conf_file(self, file):
        conf_name = {OtherFile: '资料配置', ProductFile: '图纸配置'}.get(file)
        confData = {}
        if os.path.exists(file):
            try:
                with open(file, encoding='utf-8') as f:
                    data = yaml.safe_load(f)['conf']
                    for i in data:
                        dept, key = str(i[0]).strip(), str(i[1]).strip()
                        if dept and key:
                            if key not in confData:
                                confData[key] = [dept]
                            else:
                                confData[key].append(dept)
                        else:
                            QMessageBox.warning(self.centralwidget, f'{conf_name}', '部门或关键字数据不能为空',
                                                QMessageBox.Ok)
                            return False
            except Exception as e:
                QMessageBox.warning(self.centralwidget, f'{conf_name}', '配置数据错误，请检查确认', QMessageBox.Ok)
                return False
        else:
            QMessageBox.warning(self.centralwidget, f'{conf_name}', '配置数据为空，请检查确认', QMessageBox.Ok)
            return False
        return confData

    def conf_data(self, only_hand: bool = False):
        if only_hand:
            otherData = self.read_conf_file(OtherFile)
            productData = self.read_conf_file(ProductFile)
        else:
            otherData = self.read_conf_file(OtherFile) if self.inputOneOtherFiles or self.inputTwoOtherFiles else {}
            productData = self.read_conf_file(ProductFile) \
                if self.inputOneProductFiles or self.inputTwoProductFiles else {}
        if otherData is False:
            return
        else:
            self.confSet.otherData = otherData
        if productData is False:
            return
        else:
            self.confSet.productData = productData
        return True

    def check_data(self, only_hand=False):
        # if float(datetime.datetime.now().timestamp()) >= float(base64.b64decode(self.ID.encode()).decode()):
        #     QMessageBox.warning(self.centralwidget, '错误', '试用已到期，感谢使用', QMessageBox.Ok)
        #     return
        if only_hand and not self.inputHandoutFiles:
            QMessageBox.warning(self.centralwidget, '错误', '选择分发图片不能为空', QMessageBox.Ok)
            return

        if not only_hand and not self.inputOneProductFiles and not self.inputTwoProductFiles \
                and not self.inputOneOtherFiles and not self.inputTwoOtherFiles:
            QMessageBox.warning(self.centralwidget, '错误', '图纸图片和资料图片至少有一个不为空', QMessageBox.Ok)
            return
        if not self.outputPath:
            QMessageBox.warning(self.centralwidget, '错误', '图片输出路径不能为空', QMessageBox.Ok)
            return
        if not os.path.exists(self.outputPath):
            QMessageBox.warning(self.centralwidget, '错误', f'图片输出路径不存在，请确认', QMessageBox.Ok)
            return
        sava_params = {
            '输出路径': self.outputPath,
        }
        with open('config.yml', 'w', encoding='utf-8') as f:
            yaml.safe_dump(sava_params, f, allow_unicode=True)
        return True

    @staticmethod
    def copy_pic(src: str, dst: str):
        save_dir = os.path.dirname(dst)
        # 创建目录
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        if os.path.exists(dst):
            basename = os.path.basename(dst)
            name, pic_type = basename.split('.')[0], basename.split('.')[-1]
            index = name.split('_')[-1]
            if index.isdigit():
                index = int(index) + 1
                dst = os.path.join(save_dir, f'{name.split("_")[0]}_{index}.{pic_type}')
            else:
                dst = os.path.join(save_dir, f'{name}_1.{pic_type}')
        shutil.copy(src, dst)

    def read_pic(self, pic_files: list, row: int = 0, is_one_product: bool = True):
        from ReadPic import ReadPic
        RP = ReadPic()
        key_list, dept_data = (self.confSet.other_key_list, self.confSet.otherData) if row > 0 \
            else (self.confSet.product_key_list, self.confSet.productData)
        for pic in pic_files:
            baseName = os.path.basename(pic)  # 原文件名（带后缀）
            picType = os.path.splitext(baseName)[1]  # 文件后缀名
            newName = RP.read_pic_name(pic_file=pic, row=row, only_name=is_one_product)  # 识别名称，不带后缀
            totalNewName = newName + picType  # 识别后的文件名（带后缀）
            saveDir = []  # 初始化存储目录列表
            from ReadPic import ReadRes
            if isinstance(newName, ReadRes):
                self.copy_pic(pic, os.path.join(self.savePath, '所有文件', baseName))  # 备份到所有文件
                self.copy_pic(pic, os.path.join(self.savePath, '未配置部门文件', baseName))
                self.logView.append(f'{get_time()}  {baseName}......失败：{newName.errorMsg}')
                QApplication.processEvents()
            elif newName == '':
                self.copy_pic(pic, os.path.join(self.savePath, '所有文件', baseName))  # 备份到所有文件
                self.copy_pic(pic, os.path.join(self.savePath, '未配置部门文件', baseName))
                self.logView.append(f'{get_time()}  {baseName}......失败：场景识别文本为空')
                QApplication.processEvents()
            else:
                self.successNum += 1
                self.logView.append(f'{get_time()}  {baseName}......成功')
                QApplication.processEvents()
                if totalNewName not in self.fileNameToDirDict:  # 没有同名识别名称
                    self.fileNameToDirDict.update({totalNewName: NameDir()})  # 定义图片名称，存储序号和存储目录列表的类型
                    for key in key_list:
                        # 匹配关键字
                        if key in newName:
                            saveDir.extend(dept_data.get(key))
                    if saveDir:
                        for d in set(saveDir):
                            self.copy_pic(pic, os.path.join(self.savePath, d, totalNewName))
                    else:  # 没有匹配则分配到未配置部门文件
                        saveDir.append('未配置部门文件')
                        self.copy_pic(pic, os.path.join(self.savePath, '未配置部门文件', totalNewName))
                    # 备份到所有文件
                    saveDir.append('所有文件')
                    self.copy_pic(pic, os.path.join(self.savePath, '所有文件', totalNewName))
                    self.fileNameToDirDict[totalNewName].setDirs(saveDir)  # 更新存储的所有目录
                else:
                    # 存储同名的识别图片
                    self.fileNameToDirDict[totalNewName].index_add_one()
                    Index = str(self.fileNameToDirDict[totalNewName].Index)
                    for d in self.fileNameToDirDict[totalNewName].DirList:
                        self.copy_pic(pic, os.path.join(self.savePath, d, newName + '_' + Index + picType))

    def run_main(self):
        res = True
        self.init_run()
        self.totalNum = len(self.inputOneOtherFiles + self.inputTwoOtherFiles +
                            self.inputOneProductFiles + self.inputTwoProductFiles)
        self.successNum = self.failNum = 0
        self.logView.append(f'{get_time()}  开始运行')
        QApplication.processEvents()
        self.savePath = os.path.join(self.outputPath, datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '-识别分发')
        os.mkdir(self.savePath)
        try:
            self.read_pic(pic_files=self.inputOneOtherFiles, row=1)
            self.read_pic(pic_files=self.inputTwoOtherFiles, row=2)
            self.read_pic(pic_files=self.inputOneProductFiles)
            self.read_pic(pic_files=self.inputTwoProductFiles, is_one_product=False)
        except Exception:
            res = False
        self.fileNameToDirDict = {}
        self.logView.append(
            f'{get_time()}  运行完成：总计识别图片:{self.totalNum},成功:{self.successNum},失败：{self.totalNum - self.successNum}')
        QApplication.processEvents()
        return res

    def run_read(self):
        picNames = {}
        res = True
        self.init_run()
        self.totalNum = len(
            self.inputOneOtherFiles + self.inputTwoOtherFiles + self.inputOneProductFiles + self.inputTwoProductFiles)
        self.successNum = self.failNum = 0
        self.init_run()
        self.logView.append(f'{get_time()}  开始运行')
        QApplication.processEvents()
        self.savePath = os.path.join(self.outputPath, datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '-仅识别')
        os.mkdir(self.savePath)
        save_path = os.path.join(self.savePath, '所有文件')

        from ReadPic import ReadPic
        RP = ReadPic()

        def savedPic(src: str, row: int = 0, only_name: bool = True):
            pic_name = RP.read_pic_name(pic_file=src, row=row, only_name=only_name)
            baseName = os.path.basename(src)
            type_name = '.' + baseName.split('.')[-1]
            from ReadPic import ReadRes
            if isinstance(pic_name, ReadRes):
                self.logView.append(f'{get_time()}  {baseName}......失败：{pic_name.errorMsg}')
                QApplication.processEvents()
                save_name = baseName
            else:
                self.logView.append(f'{get_time()}  {baseName}......成功')
                QApplication.processEvents()
                self.successNum += 1
                if pic_name not in picNames:
                    picNames[pic_name] = 0
                    save_name = pic_name + type_name
                else:
                    picNames[pic_name] += 1
                    save_name = f'{pic_name}_{picNames[pic_name]}{type_name}'
            self.copy_pic(src=src, dst=os.path.join(save_path, save_name))

        for pic in self.inputOneOtherFiles:
            savedPic(src=pic, row=1)
        for pic in self.inputTwoOtherFiles:
            savedPic(src=pic, row=2)
        for pic in self.inputOneProductFiles:
            savedPic(src=pic, only_name=True)
        for pic in self.inputTwoProductFiles:
            savedPic(src=pic, only_name=False)
        self.fileNameToDirDict = {}
        self.logView.append(
            f'{get_time()}  运行完成：总计识别图片:{self.totalNum},成功:{self.successNum},失败:{self.totalNum - self.successNum}')
        QApplication.processEvents()
        return res

    def handout_run(self):
        self.init_run()
        self.totalNum = len(self.inputHandoutFiles)
        self.successNum = self.failNum = 0
        self.logView.append(f'{get_time()}  开始运行')
        QApplication.processEvents()
        self.savePath = os.path.join(self.outputPath, datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '-仅分发')
        os.mkdir(self.savePath)
        for pic in self.inputHandoutFiles:
            dirs = []
            basename = os.path.basename(pic)
            pic_name, type_name = basename.split('.')[0].split('_')[0], '.' + basename.split('.')[-1]
            for i in self.confSet.product_key_list:
                if i in pic_name:
                    dirs = self.confSet.productData.get(i)
            if not dirs:
                for i in self.confSet.other_key_list:
                    if i in pic_name:
                        dirs = self.confSet.otherData.get(i)
            if dirs:
                dirs.append('所有文件')
                self.successNum += 1
            else:
                self.failNum += 1
                dirs = ['未配置部门文件', '所有文件']
            for d in set(dirs):
                self.copy_pic(pic, os.path.join(self.savePath, d, basename))
        self.logView.append(
            f'{get_time()}  运行完成，总计分发图片:{self.totalNum}，匹配:{self.successNum},未匹配:{self.failNum}')
        QApplication.processEvents()

    @log_exception
    def start_run(self):
        self.setEnabled(False)
        self.confSet = ConfSet()
        if self.check_data() and self.conf_data():
            self.run_main()
        self.setEnabled(True)

    @log_exception
    def start_read_pic(self):
        self.setEnabled(False)
        if self.check_data():
            self.run_read()
        self.setEnabled(True)

    @log_exception
    def start_hand_out(self):
        self.setEnabled(False)
        if self.check_data(only_hand=True) and self.conf_data(only_hand=True):
            self.handout_run()
        self.setEnabled(True)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
