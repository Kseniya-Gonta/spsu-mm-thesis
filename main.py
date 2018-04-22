# -*- coding: utf-8 -*-
#!/usr/bin/python
"""
Created on Wed Jan 24 15:49:36 2018
 
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

from math import degrees
 
class MainWindow(QtGui.QWidget):
    time = 0
    timer = QtCore.QTimer()
    colors = ['darkorange', 'y', 'mediumaquamarine', 'mediumorchid', 'darkgreen', 'crimson', 'gold', 'darkgrey']
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
        
        self.edit_errOfLen = QtGui.QLineEdit('5')
        self.edit_errOfLen.setFixedSize(maxSizeWidgets)
        self.edit_errOfLen.setMaxLength(3)
        
        self.edit_errOfAngle = QtGui.QLineEdit('0.9')   
        self.edit_errOfAngle.setFixedSize(maxSizeWidgets)
       
#________________________________________________________
        space = 13        
        sublayoutOptions = QtGui.QVBoxLayout()
        sublayoutOptions.setSpacing(2)
        
        sublayoutOptions.addWidget(l_time) 
        sublayoutOptions.addWidget(self.timeDisplay)
        sublayoutOptions.addSpacing(space)
        
        sublayoutOptions.addWidget(bt_start)
        sublayoutOptions.addWidget(bt_pause)
        sublayoutOptions.addSpacing(space)
                
        sublayoutOptions.addWidget(l_groupRButton)
        sublayoutOptions.addWidget(rb_algorithm1)
        sublayoutOptions.addWidget(rb_algorithm2)
        sublayoutOptions.addSpacing(space)
                
        sublayoutOptions.addWidget(l_show)
        sublayoutOptions.addWidget(self.chb_neighborhood)
        sublayoutOptions.addSpacing(space)
        
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
        
        # set the layout
        sublayoutFigure = QtGui.QVBoxLayout()
        sublayoutFigure.addWidget(self.toolbar)
        sublayoutFigure.addWidget(self.canvas)
        grid.addLayout(sublayoutFigure, 0, 1, 28, 10)
#_________________________________________________________
        
        self.setLayout(grid)
        self.resize(1000, 700)
#____________________func_init____________________________
        self.initTimer()
        self.initAgent()
        self.plot()
        self.center = cc.ComputingCenter()
    
    def bt_startClicked(self):
        self.timer.start()
        
    def changeTimeOnDisplay(self):
        self.time += 1
        self.timeDisplay.setNum(self.time)
    
    def initAgent(self):
        target1 = a.AgentTarget(70, 150, 10, 0)
        target2 = a.AgentTarget(100, 130, 10, -5)
        target3 = a.AgentTarget(120, 160, 1, 1)
        target4 = a.AgentTarget(250, 120, -10, 5)
        self.targets = [target1, target2, target3, target4]
 
        errLength = float(self.edit_errOfLen.text())
        errAngle = float(self.edit_errOfAngle.text())
        sensor1 = a.AgentSensor(50, 50, 0, 0, errLength, errAngle)
        sensor2 = a.AgentSensor(100, 60, 0, 0, errLength, errAngle)  
        sensor3 = a.AgentSensor(120, 25, 0, 0, errLength, errAngle)
        sensor4 = a.AgentSensor(150, 35, 0, 0, errLength, errAngle)
        sensor5 = a.AgentSensor(200, 10, 0, 0, errLength, errAngle)
        self.sensors = [sensor1, sensor2, sensor3, sensor4, sensor5]
        
        
    def agentsMove(self):
        for target in self.targets: 
            target.move()
        for sensor in self.sensors:
            sensor.move()
            
    def observe(self):
        for sensor in self.sensors:
            sensor.getData(self.targets)
    
    def sendToCenter(self):
        self.center.getDataFromSensors(self.sensors)
    
    def findIntersection(self):
        self.center.getIntersectionEllipses()
        
    def findIntersectionVol(self):
        self.center.bruteForce()
        
        
    def timerTick(self):
        self.changeTimeOnDisplay()
        self.agentsMove()
        self.observe()
        self.sendToCenter()
        self.findIntersectionVol()
        #self.findIntersection()
        self.plot2()
        
    def bt_pauseClicked(self):
        self.timer.stop()
        
    def plot(self):
        # create an axis
        axes = self.figure.add_subplot(111, aspect = 'auto') #Pth=1 position on a grid with R=1 rows and C=1 columns.

        # discards the old graph
        axes.clear()

        # Set / General        
        xmin, xmax = 0, 400
        ymin, ymax = 0, 300
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
        xmin, xmax = 0, 400
        ymin, ymax = 0, 300
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
            
        #add measurement
        for indexSensor in range(len(self.sensors)):
            for indexTarget in range(len(self.targets)):
                clr = self.colors[indexSensor]
                point = patches.Ellipse((self.center.xOfTarget(indexTarget, indexSensor),
                                         self.center.yOfTarget(indexTarget, indexSensor)), 
                                        1, 1, color=clr, linewidth=1)
                axes.add_patch(point)
                if self.chb_neighborhood.isChecked():
                    neighborhood = self.center.createPatchesNeighborhood(indexTarget, indexSensor, clr)
                    axes.add_patch(neighborhood)
                    
        #add intersection
#        clr = self.colors[len(self.targets)]        
#        for i in range(len(self.targets)):
#            intersection = self.center.createPathesIntersection(i, clr)
#            axes.add_patch(intersection)
                    
                    
#        indexSensor = 0
#        for dataBySensor in self.center.dataOfTargets:
#            indexTarget = 0
#            for targetData in dataBySensor:
#                point = patches.Ellipse((targetData.x, targetData.y), 1, 1, color=self.colors[indexSensor], linewidth=1)
#                axes.add_patch(point)
#                if self.chb_neighborhood.isChecked():
#                    neighborhood = self.center.createPatchesNeighborhood(indexTarget, indexSensor, self.colors[indexSensor])
#                    #neighborhood = patches.Ellipse((targetData.x, targetData.y),2 * targetData.widthOfEllipse,
#                    #                               2 * targetData.lengthOfEllipse, degrees(targetData.angle),
#                    #                              edgecolor=self.colors[indSensor], fill=False, linewidth=1)             
#                    axes.add_patch(neighborhood)
#                indexTarget += 1
#            indexSensor += 1   
            
#        index = len(self.sensors)
#        for i in self.center.intersections:
#            pattern = patches.Ellipse((i.x, i. y), 2*i.widthOfEllipse, 2*i.lengthOfEllipse,
#                                      degrees(i.angle), color = self.colors[index])
#            axes.add_patches(pattern)   
        self.canvas.draw()
       
def main():
    
    app = QtGui.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()       