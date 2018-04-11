# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 20:10:13 2018

@author: Anna Leonova
"""
import agent as a
import measurement as m
import cvxlib as cvx
import numpy as np
import math

class ComputingCenter(object):
   
    def __init__(self):
        """Constructor"""
        self._dataOfTargets = [] #list of sensor's measurements vectors

    @property
    def dataOfTargets(self):
        return self._dataOfTargets
   
    @dataOfTargets.setter
    def dataOfTargets(self, value):
        self._dataOfTargets = value
   
    def getDataFromSensors(self, sensors):
        self._dataOfTargets = []
        for sensor in sensors:
            i = 0
            dataFromSensor = []
            for target in sensor.measurements:
                point  = target.polarPoint.polarToCartesian(sensor.point)
                data = m.MeasurementFromCCenter(point.x, point.y, target.widthOfEllipse, target.lengthOfEllipse, target.angle)
                dataFromSensor.append(data)
                #print 'data of targets',i , ':', dataFromSensor[i].point.point
                i += 1
            self._dataOfTargets.append(dataFromSensor)
            
    def getIntersectionEllipses(self):
        #angle in rad
        ellipses = []
        i = 0
        for data in self._dataOfTargets:
            P = np.array([[data[i].lengthOfEllipse, 0], 
                          [0, data[i].widthOfEllipse]])
            R = np.array([[math.cos(data[i].angle), -math.sin(data[i].angle)],
                         [math.sin(data[i].angle), math.cos(data[i].angle)]]) 
            temp = np.dot(np.dot(R, P), np.transpose(R))
            e = cvx.Ellipse()
            e.initByAm(temp, data[i].point.point)
            ellipses.append(e)
        finalEllipse = cvx.findIntersection(ellipses)
        
        
            
        
