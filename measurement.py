# -*- coding: utf-8 -*-
"""
Created on Sat Jan 27 21:13:29 2018

@author: Anna Leonova
"""
import agent as a

class Measurement(object):
    
    def __init__(self, x1, x2, errLength, errAngle):
        self._point = a.Point(x1, x2)
        self._lengthOfEllipse = errLength
        self._widthOfEllipse = errAngle
       
    @property
    def point(self):
        return self._point
       
    @point.setter
    def point(self, value):
        self._point = value
 
    @property
    def x1(self):
        return self._point.x
       
    @x1.setter
    def x1(self, value):
        self._point.x = value
       
    @property
    def x2(self):
        return self._point.y
       
    @x2.setter
    def x2(self, value):
        self._point.y = value
       
    @property
    def lengthOfEllipse(self):
        return self._lengthOfEllipse
       
    @lengthOfEllipse.setter
    def lengthOfEllipse(self, value):
        self._lengthOfEllipse = value
   
    @property
    def widthOfEllipse(self):
        return self._widthOfEllipse
       
    @widthOfEllipse.setter
    def widthOfEllipse(self, value):
        self._widthOfEllipse = value

class MeasurementFromSensor(Measurement):
    
    def __init__(self, angle, dist, errLength, errAngle):
        super(MeasurementFromSensor, self).__init__(angle, dist, errLength, errAngle)
       
    @property
    def polarPoint(self):
        return self._point
       
    @polarPoint.setter
    def polarPoint(self, value):
        self._point = value
 
    @property
    def dist(self):
        return self._point.y
       
    @dist.setter
    def dist(self, value):
        self._point.y = value
       
    @property
    def angle(self):
        return self._point.x
       
    @angle.setter
    def angle(self, value):
        self._point.x = value

class MeasurementFromCCenter(Measurement):
    
    def __init__(self, x, y, errLength, errAngle, angle):
        super(MeasurementFromCCenter, self).__init__(x, y, errLength, errAngle)
        self._angle = angle
       
    @property
    def x(self):
        return self._point.x
       
    @x.setter
    def x(self, value):
        self._point.x = value   
        
    @property
    def y(self):
        return self._point.y
       
    @y.setter
    def y(self, value):
        self._point.y = value
        
    @property
    def angle(self):
        return self._angle
       
    @angle.setter
    def angle(self, value):
        self._angle = value

