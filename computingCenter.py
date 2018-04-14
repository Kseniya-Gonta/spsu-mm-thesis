# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 20:10:13 2018

@author: Anna Leonova
"""
import agent
import measurement as m
import cvxlib as cvx
import numpy as np
from matplotlib import patches

class ComputingCenter(object):
   
    def __init__(self):
        """Constructor"""
        #self._dataOfTargets = [] #list of sensor's measurements vectors
        #2d array of cvx.Ellipse, where i row - target i, j column - j sensor
        self._neighborhoods = []
        self._ellipses = []
        self._outerEllipses = []

    @property
    def outerEllipses(self):
        return self._outerEllipses
   
    @outerEllipses.setter
    def outerEllipses(self, value):
        self._outerEllipses = value      
   
    @property
    def neighborhoods(self):
        return self._neighborhoods
   
    @neighborhoods.setter
    def neighborhoods(self, value):
        self._neighborhoods = value    
    
    @property
    def getNumTargets(self):
        return self.neighborhoods.shape[0]
        
    @property
    def getNumSensors(self):
        return self.neighborhoods.shape[1]
   
    @neighborhoods.setter
    def neighborhoods(self, value):
        self._neighborhoods = value  
    
    @property
    def intersections(self):
        return self._ellipses
   
    @intersections.setter
    def intersections(self, value):
        self._ellipses = value
    
    def xOfTarget(self, indexTarget, indexSensor):
        return self._neighborhoods[indexTarget][indexSensor].x_c[0]
    
    def yOfTarget(self, indexTarget, indexSensor):
        return self._neighborhoods[indexTarget][indexSensor].x_c[1]
   
#    def getDataFromSensors(self, sensors):
#        self._dataOfTargets = []
#        for sensor in sensors:
#            i = 0
#            dataFromSensor = []
#            for target in sensor.measurements:
#                
#                data = m.MeasurementFromCCenter(point.x, point.y, target.widthOfEllipse, target.lengthOfEllipse, target.angle)
#                dataFromSensor.append(data)
#                #print 'data of targets',i , ':', dataFromSensor[i].point.point
#                i += 1
#            self._dataOfTargets.append(dataFromSensor)
   
    def getDataFromSensors(self, sensors):
        #i row - target i, j column - j sensor
        numSensors = len(sensors)
        numTargets = len(sensors[0].measurements)
        self._neighborhoods = np.empty([numTargets, numSensors], dtype = object)
        j = 0   
        for sensor in sensors:
            i = 0
            for target in sensor.measurements:
                point  = target.polarPoint.polarToCartesian(sensor.point)
                self._neighborhoods[i, j] = self.createEllipse(target, point.point)
                i += 1
            j += 1
            
    def createEllipse(self, target, point):
        #type(target) = measurementFromSensors
        angle = target.angle
        dist = target.dist
        R = np.array([[np.cos(angle), -np.sin(angle)],
                      [np.sin(angle), np.cos(angle)]])#What of kind?
        sigma_angle = target.widthOfEllipse
        sigma_distance = target.lengthOfEllipse
        P = np.array([[np.power(sigma_angle, 2), 0],
                      [0, np.power(sigma_distance, 2)]])
        #factor - The coefficient for increasing the error in angle according to the distance
        #magic constant, actually 1% of the distance value
        factor = np.array([[np.power(dist/100, 2), 0], 
                           [0,                  1]])
        P = np.dot(factor, P)
        cov = np.dot(np.dot(R, P), np.transpose(R))
        e = cvx.Ellipse()
        e.initByAm(cov, point)
        return e
    
    def createPatchesNeighborhood(self, indexTarget, indexSensor, color): 
        #type(e) = cvx.Ellipse
        e = self._neighborhoods[indexTarget, indexSensor]
    
        #Calculate the eigenvectors and eigenvalues
        covariance = e.P;
        eigenval, eigenvec = np.linalg.eig(covariance);

        #Get the largest eigenvalue
        largest_eigenval = np.amax(eigenval);        
        
        #Get the index of the largest eigenvector
        largest_eigenvec_ind = np.argmax(eigenval)
        largest_eigenvec = eigenvec[:, largest_eigenvec_ind]
        
        #Get the smallest eigenvector and eigenvalue
        if largest_eigenvec_ind == 0:
            smallest_eigenval = eigenval[1]
            #smallest_eigenvec = eigenvec[:,1]
        else:
            smallest_eigenval = eigenval[0]
            #smallest_eigenvec = eigenvec[:,0]
        
        #Calculate the angle between the x-axis and the largest eigenvector
        angle = np.arctan2(largest_eigenvec[1], largest_eigenvec[0])
        
        #This angle is between -pi and pi.
        #Let's shift it such that the angle is between 0 and 2pi
        if angle < 0:
            angle = angle + 2 * np.pi
        
        #Get the coordinates of the data mean
        avg = e.x_c;
        
        #Get the 95% confidence interval error ellipse
        chisquare_val = 5.99;
        phi = angle;
        x0 = avg[0];
        y0 = avg[1];
        a = chisquare_val * np.sqrt(largest_eigenval);
        b = chisquare_val * np.sqrt(smallest_eigenval);
        pattern = patches.Ellipse((x0, y0), 2*b, 2*a, np.degrees(phi), edgecolor = color, fill=False)
        return pattern        
        
    def getIntersectionEllipses(self):
        self.outerEllipses = []
        numTargets = self.getNumTargets()
        for i in range(numTargets):
            finalEllipse = cvx.findIntersection(self.neighborhoods[i, :])
            self.outerEllipses.append(finalEllipse)
    
    def createPathesIntersection(self, indexTarget, color):
        #type(e) = cvx.Ellipse
        e = self.outerEllipses[indexTarget]
        angle = -0.5 * np.arctan2(2*e.P[0][1], e.P[1][1]-e.P[0][0])
        R = np.array([[np.cos(angle), np.sin(angle)],
                      [-np.sin(angle), np.cos(angle)]])
        Q = np.dot(np.dot(R, e.P), np.transpose(R))
        x0, y0 = e.x_c
        pattern = patches.Ellipse((x0, y0), 2*e.Q[0, 0], 2*Q[1, 1],  np.degrees(angle),
                                  edgecolor = color, fill=False)
        return pattern 
        
    #outer boundary, result - square
    def createIntersectionBoundary(self, indexTarget):
        #type(e) = cvx.Ellipse
        e = self.outerEllipses[indexTarget]
        angle = -0.5 * np.arctan2(2*e.P[0][1], e.P[1][1]-e.P[0][0])
        R = np.array([[np.cos(angle), np.sin(angle)],
                      [-np.sin(angle), np.cos(angle)]])
        Q = np.dot(np.dot(R, e.P), np.transpose(R))
        #find size of square side
        size = 2 * np.amax(Q[0, 0], Q[1, 1])
        xCenter, yCenter = e.x_c
        return xCenter, yCenter, size
    
    def methodMonteCarlo(self, indexTarget, indSensors):
        numShots = 1000
        #find boundary
        x_c, y_c, size = self.createIntersectionBoundary(indexTarget)
        
        a = np.random.uniform(x_c-size, y_c-size, numShots)
        b = np.random.uniform(x_c-size, y_c-size, numShots)
        
        counter = 0
        for x, y in zip(a, b):
            #count those points that belong to all ellipses at once
            #if all()
            print 'hello'
            
            
    
    #def InEllipse(self, e, point):
        

    def getIntersectionEllipses0(self):#don't work!
        self.intersections = []
        #angle in rad
        ellipses = []
        i = 0
        n = len(self._dataOfTargets)
        print n
        while i < n:#on target
            for data in self._dataOfTargets:#on sensors
                P = np.array([[data[i].widthOfEllipse, 0], 
                              [0, data[i].lengthOfEllipse]])
                print 'P', P, 'angleDeg', np.degrees(data[i].angle), 'angleRad', data[i].angle, 'xy', data[i].point.point
                R = np.array([[np.cos(data[i].angle), -np.sin(data[i].angle)],
                               [np.sin(data[i].angle), np.cos(data[i].angle)]]) #ok
                temp = np.dot(np.dot(R, P), np.transpose(R))
                print 'temp', temp
                e = cvx.Ellipse()
                e.initByAm(temp, data[i].point.point)
                ellipses.append(e)
            finalEllipse = cvx.findIntersection(ellipses)
            ellipses = []
            angle = -0.5*np.arctan2(2*finalEllipse.P[0][1], finalEllipse.P[1][1]-finalEllipse.P[0][0]) #ok
            R = np.array([[np.cos(angle), np.sin(angle)],
                          [-np.sin(angle), np.cos(angle)]])#ok
            Q = np.dot(np.dot(R, finalEllipse.P), np.transpose(R))#ok
            temp = m.MeasurementFromCCenter(finalEllipse.x_c[0], finalEllipse.x_c[1],
                                            Q[0][0], Q[1][1], angle)
            self.intersections.append(temp)
            i += 1
        
            
        
