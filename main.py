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
import report as r
import computingCenter as cc

from numpy.random import uniform
 
class MainWindow(QtGui.QWidget):
    time = 0
    timer = QtCore.QTimer()
    colors = ['darkorange', 'y', 'mediumaquamarine', 'mediumorchid', 'darkgreen', 'crimson', 'gold', 'darkgrey']
    def initTimer(self):
        self.connect(self.timer, QtCore.SIGNAL('timeout()'), self.timerTick)
        self.timer.setInterval(1000)
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
 
        self.setWindowTitle('OSDASS - Optimization of Sensors Distribution Among the Signals Sources')
        self.setWindowIcon(QtGui.QIcon('icons/network.png'))
       
        #the first column of widgets in the grid
        l_input = QtGui.QLabel('Input:')
        self.rb_input_out = QtGui.QRadioButton('Host name')
        self.rb_input_out.clicked.connect(self.showDialogFile)
     
        self.rb_input_in  = QtGui.QRadioButton('Simulation')
        self.rb_input_in.toggle()
        self.rb_input_in.clicked.connect(self.simulationModeOn)
        
        self.l_input_out_path = QtGui.QLabel('there is no path')
        self.l_input_out_path.setStyleSheet("""border-style: solid; border-width: 1px;  
                                            border-color: lightgray; 
                                            background-color: rgb(226, 226, 226)""")  
       
        l_time = QtGui.QLabel('Time:')
        self.timeDisplay = QtGui.QLabel('0')
        self.timeDisplay.setStyleSheet('border-style: solid; border-width: 1px; border-color: lightgray;')
 
        bt_start =  QtGui.QPushButton('start')
        self.connect(bt_start, QtCore.SIGNAL('clicked()'), self.bt_startClicked)
        bt_pause =  QtGui.QPushButton('pause')
        self.connect(bt_pause, QtCore.SIGNAL('clicked()'), self.bt_pauseClicked)
        l_groupRButton = QtGui.QLabel('Choose an algorithm:')
        nameOfAlgorithms = ['brute force', 'by LMI', 'compare']
        self.rb_algorithm1 = QtGui.QRadioButton(nameOfAlgorithms[0])
        self.rb_algorithm2 = QtGui.QRadioButton(nameOfAlgorithms[1])
        self.rb_algorithm3 = QtGui.QRadioButton(nameOfAlgorithms[2])
        self.rb_algorithm2.toggle()
       
        l_show = QtGui.QLabel('Show:')
        self.chb_neighborhood = QtGui.QCheckBox('the neighborhoods')
        self.chb_neighborhood.toggle()
        self.chb_neighborhood.stateChanged.connect(self.plot2)
        
        self.chb_prevMeasurement = QtGui.QCheckBox('prev observations')
        self.chb_prevMeasurement.toggle()
        self.chb_prevMeasurement.stateChanged.connect(self.plot2)

        self.chb_track = QtGui.QCheckBox('object track')
        self.chb_track.toggle()
        self.chb_track.stateChanged.connect(self.plot2)

        l_parameters   = QtGui.QLabel('Parameters:')
        l_lmiAlpha     = QtGui.QLabel('LMI - alpha:')
        l_numOfSensors = QtGui.QLabel('num of sensors:')
        l_numOfTargets = QtGui.QLabel('num of targets:')
        l_errOfLength  = QtGui.QLabel('Error, length, %:')
        l_errOfAngle   = QtGui.QLabel('Error, angle, deg:')

        self.chb_stopAfterStep = QtGui.QCheckBox('stop after step')        
        self.chb_stopAfterStep.toggle()
        
        self.validatorInt = QtGui.QIntValidator()
        self.validatorDbl = QtGui.QDoubleValidator()        
        
        self.edit_numOfSensors = QtGui.QLineEdit('5')
        maxSizeWidgets = self.edit_numOfSensors.sizeHint()
        self.edit_numOfSensors.setFixedSize(maxSizeWidgets)
        self.edit_numOfSensors.setMaxLength(4)
        self.edit_numOfSensors.setValidator(self.validatorInt)
        self.edit_numOfSensors.textChanged.connect(self.check_state)
        self.edit_numOfSensors.textChanged.emit(self.edit_numOfSensors.text())
        
        self.edit_lmiAlpha = QtGui.QLineEdit('1')  
        self.edit_lmiAlpha.setFixedSize(maxSizeWidgets)
        self.edit_lmiAlpha.setMaxLength(4)
        self.edit_lmiAlpha.setValidator(self.validatorDbl)
        self.edit_lmiAlpha.textChanged.connect(self.check_state)
        self.edit_lmiAlpha.textChanged.emit(self.edit_lmiAlpha.text())
        
        self.edit_numOfTargets = QtGui.QLineEdit('4')
        self.edit_numOfTargets.setFixedSize(maxSizeWidgets)
        self.edit_numOfTargets.setMaxLength(4)
        self.edit_numOfTargets.setValidator(self.validatorInt)
        self.edit_numOfTargets.textChanged.connect(self.check_state)
        self.edit_numOfTargets.textChanged.emit(self.edit_numOfTargets.text())
        
        self.edit_errOfLen = QtGui.QLineEdit('1')
        self.edit_errOfLen.setFixedSize(maxSizeWidgets)
        self.edit_errOfLen.setMaxLength(3)
        self.edit_errOfLen.setValidator(self.validatorDbl)
        self.edit_errOfLen.textChanged.connect(self.check_state)
        self.edit_errOfLen.textChanged.emit(self.edit_errOfLen.text())
        
        self.edit_errOfAngle = QtGui.QLineEdit('0.3')   
        self.edit_errOfAngle.setFixedSize(maxSizeWidgets)
        self.edit_errOfAngle.setValidator(self.validatorDbl)
        self.edit_errOfAngle.textChanged.connect(self.check_state)
        self.edit_errOfAngle.textChanged.emit(self.edit_errOfAngle.text())
        
        self.bt_generate = QtGui.QPushButton('generate')
        self.bt_generate.clicked.connect(self.initAgent)
       
#________________________________________________________
        space = 13        
        sublayoutOptions = QtGui.QVBoxLayout()
        sublayoutOptions.setSpacing(2)

        sublayoutOptions.addWidget(l_input)
        sublayoutOptions.addWidget(self.rb_input_in)
        sublayoutOptions.addWidget(self.rb_input_out)
        sublayoutOptions.addWidget(self.l_input_out_path)
        sublayoutOptions.addSpacing(space)
        
        sublayoutOptions.addWidget(l_time) 
        sublayoutOptions.addWidget(self.timeDisplay)
        sublayoutOptions.addSpacing(space)
        
        sublayoutOptions.addWidget(bt_start)
        sublayoutOptions.addWidget(bt_pause)
        sublayoutOptions.addSpacing(space)
                
        sublayoutOptions.addWidget(l_groupRButton)
        sublayoutOptions.addWidget(self.rb_algorithm1)
        sublayoutOptions.addWidget(self.rb_algorithm2)
        sublayoutOptions.addWidget(self.rb_algorithm3)
        sublayoutOptions.addSpacing(space)
                
        sublayoutOptions.addWidget(l_show)
        sublayoutOptions.addWidget(self.chb_neighborhood)
        sublayoutOptions.addWidget(self.chb_prevMeasurement)
        sublayoutOptions.addWidget(self.chb_track)
        sublayoutOptions.addSpacing(space)
        
        sublayoutOptions.addWidget(l_parameters)
        sublayoutOptions.addWidget(self.chb_stopAfterStep)
        sublayoutOptions.addWidget(l_lmiAlpha)
        sublayoutOptions.addWidget(self.edit_lmiAlpha)
        sublayoutOptions.addWidget(l_numOfSensors)
        sublayoutOptions.addWidget(self.edit_numOfSensors)
        sublayoutOptions.addWidget(l_numOfTargets)
        sublayoutOptions.addWidget(self.edit_numOfTargets)
        sublayoutOptions.addWidget(l_errOfLength)
        sublayoutOptions.addWidget(self.edit_errOfLen)
        sublayoutOptions.addWidget(l_errOfAngle)
        sublayoutOptions.addWidget(self.edit_errOfAngle)
        sublayoutOptions.addWidget(self.bt_generate)
#_________________________________________________________  
         
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        grid.addLayout(sublayoutOptions, 0, 0, 23, 1)
       
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
        #self.initAgent()
        #self.plot()
        self.center = cc.ComputingCenter()
    
    def bt_startClicked(self):
        self.timer.start()
    
    def simulationModeOn(self):
        self.l_input_out_path.setText('there is no path')
        self.l_input_out_path.setStyleSheet("""border-style: solid; border-width: 1px;  
                                                border-color: lightgray; 
                                                background-color: rgb(226, 226, 226)""")
        self.bt_generate.setEnabled(True)
            
    def check_state(self, *args, **kwargs):
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QtGui.QValidator.Acceptable:
            color = '#c4df9b' # green
        elif state == QtGui.QValidator.Intermediate:
            color = '#fff79a' # yellow
        else:
            color = '#f6989d' # red
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)
        
    def generate(self):
        numTarget = int(self.edit_numOfTargets.text())
        numSensor = int(self.edit_numOfSensors.text())
        incX = 10
        lowLim_x, upLim_x = -3, 3
        lowLim_y, upLim_y = -25, 30
        
        init_x, init_y, dx, dy = 10, 30, 0, 0
        errLength = float(self.edit_errOfLen.text())
        errAngle = float(self.edit_errOfAngle.text())
        self.sensors = []
        for j in range(numSensor):
            r_x = uniform(lowLim_x, upLim_x)
            r_y = uniform(lowLim_y, upLim_y)
            init_x += incX
            x = init_x + r_x
            y = init_y + r_y
            sensor = a.AgentSensor(x, y, dx, dy, errLength, errAngle)
            self.sensors.append(sensor)
            
        init_x, init_y = 10, 200
        lowLim_dx, upLim_dx = -3, 3
        lowLim_dy, upLim_dy = -1, 1
        self.targets = []
        for i in range(numTarget):
            r_x = uniform(lowLim_x, upLim_x)
            r_y = uniform(lowLim_y, upLim_y)
            r_dx = uniform(lowLim_dx, upLim_dx)
            r_dy = uniform(lowLim_dy, upLim_dy)
            init_x += incX
            x = init_x + r_x
            y = init_y + r_y
            target = a.AgentTarget(x, y, r_dx, r_dy)
            self.targets.append(target)
        self.plot()
            
        
    def showDialogFile(self):
        self.bt_generate.setEnabled(False)
        try:
            defPath = 'D:\\\\'
            fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', defPath)
            if len(fname) == 0:
                self.rb_input_in.toggle()
            else:
                self.l_input_out_path.setStyleSheet("""border-style: solid; border-width: 1px;  
                                                    border-color: lightgray; 
                                                    background-color: rgb(255, 255, 255)""")
                self.l_input_out_path.setText(fname[0:15] + '...')     
            #testcode
            self.report = r.ReportWindow()  
            self.report.show()                              
        except:
            self.rb_input_in.toggle()
            self.simulationModeOn()
        
    def changeTimeOnDisplay(self):
        self.time += 1
        self.timeDisplay.setNum(self.time)
    
    def initAgent(self):
        target1 = a.AgentTarget(70, 210, 3, 0)
        target2 = a.AgentTarget(100, 190, 3, -1)
        target3 = a.AgentTarget(120, 220, 1, 1)
        target4 = a.AgentTarget(250, 180, -3, 1)

        self.targets = [target1, target2, target3, target4]
        
        errLength = float(self.edit_errOfLen.text())
        errAngle = float(self.edit_errOfAngle.text())
        sensor1 = a.AgentSensor(50, 50, 0, 0, errLength, errAngle)
        sensor2 = a.AgentSensor(100, 60, 0, 0, errLength, errAngle)  
        sensor3 = a.AgentSensor(120, 25, 0, 0, errLength, errAngle)
        sensor4 = a.AgentSensor(150, 35, 0, 0, errLength, errAngle)
        sensor5 = a.AgentSensor(200, 10, 0, 0, errLength, errAngle)

        self.sensors = [sensor1, sensor2, sensor3, sensor4, sensor5]
        self.plot()          
        
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
        alpha = float(self.edit_lmiAlpha.text())
        if self.rb_algorithm2.isChecked():
            try:
                self.center.solveByLMI(alpha)
            except Exception:
                print 'LMI don\'t work :c'
                print Exception
        elif self.rb_algorithm1.isChecked(): 
            self.center.bruteForceT(alpha)
        elif self.rb_algorithm3.isChecked():
            try:
                self.center.solveByLMI(alpha)
                self.center.bruteForce(alpha)
            except Exception:
                print 'LMI don\'t work :c'
                print Exception
                
        if self.chb_stopAfterStep.isChecked():
            self.timer.stop()
            
        
    def findIntersectionVol(self):
        self.center.bruteForce()
             
    def timerTick(self):
        self.changeTimeOnDisplay()
        self.agentsMove()
        self.observe()
        self.sendToCenter()
        #self.findIntersectionVol()
        self.findIntersection()
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
        
        clr = 'steelblue'
        for target in self.targets:
            pattern = patches.Ellipse((target.x, target.y), width, height, 0, facecolor='powderblue', edgecolor='steelblue', linewidth=1)
            arrow = patches.Arrow(target.x, target.y, target.dx / abs(target.dx) * height, target.dy / abs(target.dx) * height, lenArrow, color='steelblue')        
            axes.add_patch(pattern)
            axes.add_patch(arrow)
            if self.chb_track.isChecked():
                for p in target.track:
                    point = patches.Ellipse((p.x, p.y), 1, 1, color=clr, linewidth=1)
                    axes.add_patch(point)
                
            
        #add previous measurement
        if self.chb_prevMeasurement.isChecked():
            clr = 'lightcoral'
            for m in self.center.prevMeasurement:
                point = patches.Ellipse((m.x, m.y), 1, 1, color=clr, linewidth=1)
                axes.add_patch(point)
            
        #add measurement
        for indexSensor in range(len(self.sensors)):
            for indexTarget in range(len(self.targets)):
                clr = 'red'
                #clr = self.colors[indexSensor]
                point = patches.Ellipse((self.center.xOfTarget(indexTarget, indexSensor),
                                         self.center.yOfTarget(indexTarget, indexSensor)), 
                                        1, 1, color=clr, linewidth=1)
                axes.add_patch(point)
                if self.chb_neighborhood.isChecked():
                    neighborhood = self.center.createPatchesNeighborhood(indexTarget, indexSensor, clr)
                    axes.add_patch(neighborhood)
                    
        #add intersection
        clr = 'red'       
        for i in range(len(self.targets)):
            intersection = self.center.createPathesIntersection(i, clr)
            axes.add_patch(intersection)
                    
                    
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