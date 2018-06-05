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
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        self.setWindowTitle('Report')
        self.l_name = QtGui.QLabel('Report: ' + now.__str__())
        
        #defStr_vol = 'Total volume: '
        #defStr_FQ  = 'Functional of quality: '
        defStr_con = 'Confidence level: 95%'
        defStr_est = 'Total volume / Confidence: '
        #self.l_vol = QtGui.QLabel(defStr_vol)
        #self.l_FQ  = QtGui.QLabel(defStr_FQ)
        self.l_con = QtGui.QLabel(defStr_con)
        self.l_est = QtGui.QLabel(defStr_est)
        
        #____test____
        #vol = 48.5 / (1 - 3*0.05) + 43.5 / (1 - 3*0.05) + 93.1 / (1 - 3*0.05) + 32.6 / (1 - 3*0.5)
        vol = 38.2 / (1-0.05*5) + 36.2800 / (1-0.05*3) + 53.9200 / (1-0.05*6) + 55.1200 / (1-0.05*6)           
        FQ  = vol + 2 + 2 + 2 + 2
        self.l_est.setText(defStr_est + '%0.4f' % vol)
        #self.l_FQ.setText(defStr_FQ + '%0.4f' % FQ)
        
        defStr_alg = 'Algorithm: '
        self.l_alg = QtGui.QLabel(defStr_alg)  
        self.l_alg.setText(defStr_alg + 'Brute Force')
        
        self.table = QtGui.QTableWidget(self)
        self.table.setRowCount(4)
        self.table.setColumnCount(1)
        
        #Enter data into table
        l = 0        
        for n in range(2):
            for m in range(2):
                l += 1
                newItem = QtGui.QTableWidgetItem(l.__str__())
                self.table.setItem(m, n, newItem)
                
        #_______test: Enter data into table
#        newItem = QtGui.QTableWidgetItem('0, 1')
#        self.table.setItem(0,0, newItem)
#        
#        newItem = QtGui.QTableWidgetItem('1, 4')
#        self.table.setItem(1,0, newItem)
#        
#        newItem = QtGui.QTableWidgetItem('1, 4')
#        self.table.setItem(2,0, newItem)
#
#        newItem = QtGui.QTableWidgetItem('1, 4')
#        self.table.setItem(3,0, newItem)

        #_______test: Enter data into table BF
        newItem = QtGui.QTableWidgetItem('0, 1, 2, 3, 4')
        self.table.setItem(0,0, newItem)
        
        newItem = QtGui.QTableWidgetItem('0, 2, 4')
        self.table.setItem(1,0, newItem)
        
        newItem = QtGui.QTableWidgetItem('0, 1, 2, 3, 4')
        self.table.setItem(2,0, newItem)

        newItem = QtGui.QTableWidgetItem('0, 1, 3, 4')
        self.table.setItem(3,0, newItem)
        
        self.table.setHorizontalHeaderLabels(['tracking group'])   
        vHeader = ['target 0', 'target 1', 'target 2', 'target 3']
        self.table.setVerticalHeaderLabels(vHeader)
        
        sublayout = QtGui.QVBoxLayout()
        sublayout.addWidget(self.l_name)
        sublayout.addWidget(self.l_alg)
        sublayout.addWidget(self.l_con) 
        sublayout.addWidget(self.l_est)
#        sublayout.addWidget(self.l_FQ)
        sublayout.addWidget(self.table)
        
        self.setLayout(sublayout)
        self.setWindowIcon(QtGui.QIcon('icons/network.png'))

def main():
    app = QtGui.QApplication(sys.argv)
    mainWindow = ReportWindow()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()       