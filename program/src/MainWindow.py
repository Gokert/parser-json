import os
import json
import colorama
import mimetypes

from PySide6.QtWidgets import QTreeView, QHeaderView, QMainWindow, QFileDialog, QMessageBox, QWidget, QVBoxLayout, QTextEdit
from PySide6.QtCore import QFile, QDateTime, QMutex
from PyQt6 import QtGui

from src.PyJson import JsonModel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        colorama.init()
        self.file_path = ''
        self.document = ''
        self._json_file = ''
        self.main_window = QWidget()
        self.view = QTreeView()
        self.text_result = QTextEdit()
        self.model = JsonModel(main_window=self)
        self.setWindowTitle("Vekas")
        self.mutex = QMutex()

        self.file_menu = self.menuBar().addMenu("File")
        self.save_button = self.file_menu.addAction("Save")
        self.open_button = self.file_menu.addAction("Open")

        self.save_button.triggered.connect(self.saveJson)
        self.open_button.triggered.connect(self.openJsonWithOS)

        self.view.setModel(self.model)
        self.setStyle()

        self.view.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.view.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.view.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        self.vbox = QVBoxLayout(self.main_window)
        self.vbox.addWidget(self.view)
        self.vbox.addWidget(self.text_result)
        self.setCentralWidget(self.main_window)

        path_configuration = self.getPathToConfiguration()
        if path_configuration !=False:
            try:
                with open(path_configuration, 'r') as file:
                    last_file_json_path = file.readline().split('=')[1]
                    if last_file_json_path.rstrip() != "None":
                        self.openJson(last_file_json_path.rstrip())
            except Exception as ex:
                self.insertPlainText(f"JSON parsing error: {ex}", True)
        else:
            self.insertPlainText(f"Configuration file not found", True)
            self.openJsonWithOS()

    def closeEvent(self, event: QtGui.QCloseEvent):
        """Called when the window is closed"""

        new_json = self.model.toJson()

        if new_json == self.document:
            exit()
        else:
            reply = QMessageBox.question(self, 'Exit confirmation',
                                         'Are you sure you want to exit without saving changes?',
                                         QMessageBox.StandardButtons.Save | QMessageBox.StandardButtons.Close | QMessageBox.StandardButtons.Cancel)

            if reply == QMessageBox.StandardButtons.Save:
                if self.saveJson(True) == True:
                    event.accept()
                else:
                    event.ignore()
            elif reply == QMessageBox.StandardButtons.Close:
                self.insertPlainText("Exit")
                exit()
            else:
                event.ignore()

    def saveJson(self, check_equivalent=False):
        """Saving a file"""

        new_json = self.model.toJson()

        file_name = ''
        try:
            file_name = self._json_file.split('/')[-1]
        except Exception as ex:
            self.insertPlainText("Missing path in configuration", True)

        if check_equivalent == True:
            if not self.saveDump(new_json, file_name):
                return False
        elif file_name == '':
            self.insertPlainText("Select a file")
        elif new_json != self.document:
            if not self.saveDump(new_json, file_name):
                return False
        else:
            self.insertPlainText(f"No changes were detected in the file {file_name}")

        return True

    def openJsonWithOS(self):
        file_path, _ = QFileDialog.getOpenFileName(None, 'Choose file', '', 'All files (*.*)')
        self.openJson(file_path)

    def openJson(self, file_path):
        """opening json"""

        mime_type, encoding = mimetypes.guess_type(file_path)

        if file_path == '':
            return
        elif mime_type != 'application/json':
            self.insertPlainText(f"File '{file_path.rstrip()}' is not json", True)
            return
        elif os.path.exists(file_path):
            self.insertPlainText(f"File '{file_path}' exist")
        else:
            self.insertPlainText(f"File '{file_path}' does not exist", True)
            return

        self._json_file = file_path
        path_configuration = self.getPathToConfiguration()

        with open(path_configuration, 'w') as file:
            file.writelines(f"last_path_to_json_file={self._json_file}")

        try:
            with open(self._json_file) as file:
                self.document = json.load(file)
                self.model.load(self.document)
        except json.JSONDecodeError as ex:
            self.insertPlainText(f"JSON parsing error: {ex}", True)

    def setStyle(self):
        """Setting CSS styles for UI"""
        path = f'{os.getcwd()}/static/template.css'

        if os.path.exists(path) == False:
            self.insertPlainText(f"{path} CSS not found", True)

        self.applyStylesheet(self.view, path)
        self.applyStylesheet(self, path)
        self.applyStylesheet(self.view.header(), path)
        self.applyStylesheet(self.text_result, path)
        self.applyStylesheet(self.menuBar(), path)
        self.applyStylesheet(self.file_menu, path)

    def applyStylesheet(self, widget, filepath):
        file = QFile(filepath)
        if file.open(QFile.OpenMode.ReadOnly | QFile.OpenMode.Text):
            style_sheet = file.readAll().data().decode("utf-8")
            widget.setStyleSheet(style_sheet)
            file.close()

    def resizeInputColoumnNumberOne(self):
        self.view.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)

    def insertPlainText(self, string, red_text=False):
        """Outputting text to the console and to the application"""
        self.mutex.lock()
        time_string = QDateTime.currentDateTime().toString("hh:mm:ss")
        if red_text == False:
            self.text_result.setTextColor("black")
            self.text_result.insertPlainText(f"{time_string}: {string}\n")
            print(f"{time_string}: {string}")
        else:
            self.text_result.setTextColor("red")
            self.text_result.insertPlainText(f"{time_string}: {string}\n")
            print(colorama.Fore.RED + f"{time_string}: {string}" + colorama.Fore.RESET)
        self.mutex.unlock()
    def getPathToConfiguration(self):
        path = f'{os.getcwd()}/configuration'
        if os.path.exists(path):
            return path
        else:
            return False

    def saveDump(self, new_json, file_name):
        with open(self._json_file, 'w') as file:
            self.document = new_json
            json.dump(new_json, file, indent=2)

        self.insertPlainText(f"Json file {file_name} has been saved")



