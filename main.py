# -*- coding: utf-8 -*-
#!/usr/bin/python
"""
Created on Sat Jan 24 15:49:36 2018
 
@author: leonova Anna
"""
import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib import patches

import agent as a
import computingCenter as cc

import random
from math import degrees
 
class MainWindow(QtGui.QWidget):
    time = 0
    timer = QtCore.QTimer()
    
    def initTimer(self):
        self.connect(self.timer, QtCore.SIGNAL('timeout()'), self.timerTick)
        self.timer.setInterval(1000)
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
 
        self.setWindowTitle('task visualization')
        self.setWindowIcon(QtGui.QIcon('icons/network.png'))
       
        #the first column of widgets in the grid
        l_time = QtGui.QLabel('Discrete time:')
        self.timeDisplay = QtGui.QLabel('0')
        self.timeDisplay.setStyleSheet('border-style: solid; border-width: 1px; border-color: lightgray;')
 
        bt_start =  QtGui.QPushButton('start')
        self.connect(bt_start, QtCore.SIGNAL('clicked()'), self.bt_startClicked)
        bt_pause =  QtGui.QPushButton('pause')
        self.connect(bt_pause, QtCore.SIGNAL('clicked()'), self.bt_pauseClicked)
        l_groupRButton = QtGui.QLabel('Choose an algorithm:')
        nameOfAlgorithms = ['brute force', 'by LMI']
        rb_algorithm1 = QtGui.QRadioButton(nameOfAlgorithms[0])
        rb_algorithm2 = QtGui.QRadioButton(nameOfAlgorithms[1])
        rb_algorithm2.toggle()
       
        l_show = QtGui.QLabel('Show:')
        self.chb_neighborhood = QtGui.QCheckBox('the neighborhood')
        self.chb_neighborhood.toggle()
        #self.chb_neighborhood.stateChanged.connect()
       
        l_parameters = QtGui.QLabel('Parameters:')
        l_numOfSensors = QtGui.QLabel('num of sensors:')
        l_numOfTargets = QtGui.QLabel('num of targets:')
        l_errOfLength = QtGui.QLabel('Error, length, %:')
        l_errOfAngle = QtGui.QLabel('Error, angle, deg:')
        
        self.edit_numOfSensors = QtGui.QLineEdit('2')
        maxSizeWidgets = self.edit_numOfSensors.sizeHint()
        self.edit_numOfSensors.setFixedSize(maxSizeWidgets)
        self.edit_numOfSensors.setMaxLength(4)
        
        self.edit_numOfTargets = QtGui.QLineEdit('1')
        self.edit_numOfTargets.setFixedSize(maxSizeWidgets)
        self.edit_numOfTargets.setMaxLength(4)
        
        self.edit_errOfLen = QtGui.QLineEdit('10')
        self.edit_errOfLen.setFixedSize(maxSizeWidgets)
        self.edit_errOfLen.setMaxLength(3)
        
        self.edit_errOfAngle = QtGui.QLineEdit('0.7')   
        self.edit_errOfAngle.setFixedSize(maxSizeWidgets)
       
#________________________________________________________
        sublayoutOptions = QtGui.QVBoxLayout()
        sublayoutOptions.setSpacing(2)
        
        sublayoutOptions.addWidget(l_time) 
        sublayoutOptions.addWidget(self.timeDisplay)
        sublayoutOptions.addSpacing(13)
        
        sublayoutOptions.addWidget(bt_start)
        sublayoutOptions.addWidget(bt_pause)
        sublayoutOptions.addSpacing(13)
                
        sublayoutOptions.addWidget(l_groupRButton)
        sublayoutOptions.addWidget(rb_algorithm1)
        sublayoutOptions.addWidget(rb_algorithm2)
        sublayoutOptions.addSpacing(13)
                
        sublayoutOptions.addWidget(l_show)
        sublayoutOptions.addWidget(self.chb_neighborhood)
        sublayoutOptions.addSpacing(13)
        
        sublayoutOptions.addWidget(l_parameters)
        sublayoutOptions.addWidget(l_numOfSensors)
        sublayoutOptions.addWidget(self.edit_numOfSensors)
        sublayoutOptions.addWidget(l_numOfTargets)
        sublayoutOptions.addWidget(self.edit_numOfTargets)
        sublayoutOptions.addWidget(l_errOfLength)
        sublayoutOptions.addWidget(self.edit_errOfLen)
        sublayoutOptions.addWidget(l_errOfAngle)
        sublayoutOptions.addWidget(self.edit_errOfAngle)
#_________________________________________________________  
         
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        grid.addLayout(sublayoutOptions, 0, 0, 21, 1)
       
#_________________________________________________________     
         # a figure instance to plot on
        self.figure = Figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Just some button connected to `plot` method
        #self.button = QtGui.QPushButton('Plot')
        #self.button.clicked.connect(self.plot)
        
        # set the layout
        sublayoutFigure = QtGui.QVBoxLayout()
        sublayoutFigure.addWidget(self.toolbar)
        sublayoutFigure.addWidget(self.canvas)
        #sublayoutFigure.addWidget(self.button)
        grid.addLayout(sublayoutFigure, 0, 1, 28, 10)
#_________________________________________________________
        
        self.setLayout(grid)
        self.resize(1000, 700)
#____________________func_init____________________________
        self.initTimer()
        self.initAgent()
        self.plot()
        self.cCenter = cc.ComputingCenter()
    
    def bt_startClicked(self):
        self.timer.start()
        
    def changeTimeOnDisplay(self):
        self.time += 1
        self.timeDisplay.setNum(self.time)
    
    def initAgent(self):
        target1 = a.AgentTarget(200, 300, 25, 0)
        target2 = a.AgentTarget(500, 200, -25, 0)
        self.targets = [target1, target2]
 
        errLength = float(self.edit_errOfLen.text())
        errAngle = float(self.edit_errOfAngle.text())
        sensor1 = a.AgentSensor(100, 100, 0, 0, errLength, errAngle)
        sensor2 = a.AgentSensor(200, 120, 0, 0, errLength, errAngle)  
        sensor3 = a.AgentSensor(400, 50, 0, 0, errLength, errAngle)
        self.sensors = [sensor1, sensor2, sensor3]
        
        
    def agentsMove(self):
        for target in self.targets: 
            target.move()
        for sensor in self.sensors:
            sensor.move()
            
    def observe(self):
        for sensor in self.sensors:
            sensor.getData(self.targets)
    
    def sendToCenter(self):
        self.cCenter.getDataFromSensors(self.sensors)
        
    def timerTick(self):
        self.changeTimeOnDisplay()
        self.agentsMove()
        self.observe()
        self.sendToCenter()
        self.plot2()
        
    def bt_pauseClicked(self):
        self.timer.stop()
        
    def plot(self):
        ''' plot some random stuff '''
        # random data
        data = [random.random() for i in range(10)]
        # create an axis
        axes = self.figure.add_subplot(111, aspect = 'auto') #Pth=1 position on a grid with R=1 rows and C=1 columns.

        # discards the old graph
        axes.clear()

        # Set / General        
        xmin, xmax = 0, 600
        ymin, ymax = 0, 500
        axes.set_xlim(xmin, xmax)
        axes.set_xlabel('X')
        axes.set_ylim(ymin, ymax)
        axes.set_ylabel('Y')

        #add agent
        width, height = 5, 5
        lenArrow = 3
        for sensor in self.sensors:
            pattern = patches.Ellipse((sensor.x, sensor.y), width, height, 0, facecolor='indianred', edgecolor='firebrick', linewidth=1)
            axes.add_patch(pattern)
        
        for target in self.targets:
            pattern = patches.Ellipse((target.x, target.y), width, height, 0, facecolor='powderblue', edgecolor='steelblue', linewidth=1)
            arrow = patches.Arrow(target.x, target.y, target.dx / abs(target.dx) * height, target.dy / abs(target.dx) * height, lenArrow, color='steelblue')        
            axes.add_patch(pattern)
            axes.add_patch(arrow)
        # plot data
        #axes.plot(data)
        # refresh canvas
        self.canvas.draw()
        
    def plot2(self):
        # create an axis        
        axes = self.figure.add_subplot(111, aspect = 'auto') #Pth=1 position on a grid with R=1 rows and C=1 columns.

        # discards the old graph
        axes.clear()

        # Set / General        
        xmin, xmax = 0, 600
        ymin, ymax = 0, 500
        axes.set_xlim(xmin, xmax)
        axes.set_xlabel('X')
        axes.set_ylim(ymin, ymax)
        axes.set_ylabel('Y')

        #add agent
        width, height = 5, 5
        lenArrow = 3
        for sensor in self.sensors:
            pattern = patches.Ellipse((sensor.x, sensor.y), width, height, 0, facecolor='indianred', edgecolor='firebrick', linewidth=1)
            axes.add_patch(pattern)
        
        for target in self.targets:
            pattern = patches.Ellipse((target.x, target.y), width, height, 0, facecolor='powderblue', edgecolor='steelblue', linewidth=1)
            arrow = patches.Arrow(target.x, target.y, target.dx / abs(target.dx) * height, target.dy / abs(target.dx) * height, lenArrow, color='steelblue')        
            axes.add_patch(pattern)
            axes.add_patch(arrow)
        
        for dataBySensor in self.cCenter.dataOfTargets:
            for targetData in dataBySensor:
                point = patches.Ellipse((targetData.x, targetData.y), 1, 1, color='orange', linewidth=1)
                axes.add_patch(point)
                if self.chb_neighborhood.isChecked():
                    neighborhood = patches.Ellipse((targetData.x, targetData.y),2 * targetData.widthOfEllipse, 2 * targetData.lengthOfEllipse, degrees(targetData.angle), edgecolor='orange', fill=False, linewidth=1)
                    print targetData.angle                    
                    axes.add_patch(neighborhood)
        # plot data
        #axes.plot(data)
        # refresh canvas
        self.canvas.draw()
       
def main():
    
    app = QtGui.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()       