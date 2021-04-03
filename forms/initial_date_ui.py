from PyQt5.QtWidgets import (QWidget, QPushButton, QLineEdit, QInputDialog, QApplication, QLabel, QGridLayout, QDialog,
                             QGroupBox, QVBoxLayout)
from PyQt5 import QtCore, QtWidgets
import sys


class InitDateForm(QDialog):
    date_edit = None
    ok_button = None
    current_date = None

    def __init__(self):
        super().__init__()
        self.title = 'Initial Date Picker'
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 100
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.gbox = QGroupBox("Pick a Initial Date")
        layout = QGridLayout()
        layout.setColumnStretch(1, 4)

        self.date_edit = QtWidgets.QDateTimeEdit()
        self.date_edit.setDateTime(QtCore.QDateTime.currentDateTime())

        self.date_edit.setCalendarPopup(True)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.select_date)

        layout.addWidget(self.date_edit, 0, 0)
        layout.addWidget(self.ok_button, 0, 1)
        self.gbox.setLayout(layout)

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.gbox)
        self.setLayout(windowLayout)

    def select_date(self):
        # print(date)
        print(self.date_edit.dateTime())
        self.current_date = self.date_edit.dateTime()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = InitDateForm()
    ex.show()
    sys.exit(app.exec_())
