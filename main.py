# -*- coding: utf-8 -*-
import sys
import os

from AppUtils import get_resource_path, get_config_path, get_exe_path, create_path_it_not_exist

from AppUI import Ui_MainWindow
from PySide2.QtWidgets import (QApplication, QDialog, QMainWindow)
from PySide2.QtGui import QIcon, QIntValidator
from PySide2.QtCore import Qt

APP_NAME = "Pyside App"
APP_CONFIG_FOLDER = "Pyside App"


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(get_resource_path(os.path.join('resources', 'icon.ico'))))

        self.configPath = create_path_it_not_exist(os.path.join(get_config_path(APP_CONFIG_FOLDER), 'config.ini')) 

        self.update_ui()

    def update_ui(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
