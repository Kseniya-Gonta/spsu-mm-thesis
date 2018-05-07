# -*- coding: utf-8 -*-
"""
Created on Mon Mar 05 04:50:34 2018

@author: User
"""
import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
import datetime

class ReportWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        now = datetime.datetime.now()
        now = now.strftime("%Y-%m-%d %H-%M-%S")
        self.setWindowTitle('Report')
        self.l_name = QtGui.QLabel('Report: ' + now.__str__())
        
        self.table = QtGui.QTableWidget(self)
        self.table.setRowCount(2)
        self.table.setColumnCount(2)
        
        #Enter data into table
        l = 0        
        for n in range(2):
            for m in range(2):
                l += 1
                newItem = QtGui.QTableWidgetItem(l.__str__())
                self.table.setItem(m, n, newItem)
        
        sublayout = QtGui.QVBoxLayout()
        sublayout.addWidget(self.l_name)
        sublayout.addWidget(self.table)
        
        self.setLayout(sublayout)
        self.setWindowIcon(QtGui.QIcon('icons/network.png'))
        self.resize(333, 370)

def main():
    app = QtGui.QApplication(sys.argv)
    mainWindow = ReportWindow()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()       