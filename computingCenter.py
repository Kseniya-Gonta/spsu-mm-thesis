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
import datetime
import time

class ComputingCenter(object):
   
    def __init__(self):
        """Constructor"""
        #self._dataOfTargets = [] #list of sensor's measurements vectors
        #2d array of cvx.Ellipse, where i row - target i, j column - j sensor
        self._neighborhoods = []
        self._prevMeasurements = []
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
    
    @property
    def intersections(self):
        return self._ellipses
   
    @intersections.setter
    def intersections(self, value):
        self._ellipses = value
        
    @property
    def prevMeasurement(self):
        return self._prevMeasurements
   
    @prevMeasurement.setter
    def prevMeasurement(self, value):
        self._prevMeasurements = value
    
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
                self._prevMeasurements.append(point)
                self._neighborhoods[i, j] = self.createEllipse(target, point.point)
                i += 1
            j += 1
            
    def createEllipse(self, target, point):
        #type(target) = measurementFromSensors
        angle = target.angle
        dist = target.dist
        #Anticlockwise rotation matrix
        R = np.array([[np.cos(angle), -np.sin(angle)],
                      [np.sin(angle), np.cos(angle)]])
        sigma_angle = np.degrees(target.widthOfEllipse) #degrees
        sigma_distance = target.lengthOfEllipse
        P = np.array([[np.power(sigma_angle, 2), 0],
                      [0, np.power(sigma_distance, 2)]])
                      
        #factor - The coefficient for increasing the error in angle according to the distance
        #magic constant, actually 1% of the distance value
        factor = np.array([[np.power(dist/100, 2), 0], 
                           [0,                     1]])
        P = np.dot(factor, P)
        covariance = np.dot(np.dot(R, P), np.transpose(R))
        
        #Calculate the eigenvectors and eigenvalues
        eigenval, eigenvec = np.linalg.eig(covariance);

        #Get the largest eigenvalue
        largest_eigenval = np.amax(eigenval);        
        
        #Get the index of the largest eigenvector
        largest_eigenvec_ind = np.argmax(eigenval)
        largest_eigenvec = eigenvec[:, largest_eigenvec_ind]
        
        #Get the smallest eigenvalue
        if largest_eigenvec_ind == 0:
            smallest_eigenval = eigenval[1]
        else:
            smallest_eigenval = eigenval[0]
        
        #Calculate the angle between the x-axis and the largest eigenvector
        angle = -np.arctan2(largest_eigenvec[0], largest_eigenvec[1])#why -???
        
        #This angle is between -pi and pi.
        #Let's shift it such that the angle is between 0 and 2pi
#        if angle < 0:
#            angle = angle + 2 * np.pi
        
        #Get the coordinates of the data mean
        avg = point;
        
        #Get the 95% confidence interval error ellipse
        chisquare_val = 5.99;
        phi = angle;
        x0 = avg[0];
        y0 = avg[1];
        a = chisquare_val * np.sqrt(largest_eigenval);
        b = chisquare_val * np.sqrt(smallest_eigenval);
        #print 'x,y', x0, y0, 'a,b', a, b,'phi', np.degrees(phi)
        #print 'b,s', largest_eigenval, smallest_eigenval 
        
        #Create cvx.Ellipse        
        P = np.array([[a, 0],
                      [0, b]])
        #Anticlockwise rotation matrix
        R = np.array([[np.cos(angle), -np.sin(angle)],
                      [np.sin(angle), np.cos(angle)]])
        P = np.dot(np.dot(R, P), np.transpose(R))
        e = cvx.Ellipse()
        e.initByAm(P, point)
        return e
        
    def getDataPatchesEllipse(self, e):
        #type(e) = cvx.Ellipse
        #Calculate the angle between the x-axis and the largest semiaxis
        angle = -0.5 * np.arctan2(2*e.P[0][1], e.P[1][1]-e.P[0][0]) + np.pi/2
        #Clockwise rotation matrix
        R = np.array([[np.cos(angle), np.sin(angle)],
                      [-np.sin(angle), np.cos(angle)]])
        Q = np.dot(np.dot(R, e.P), np.transpose(R))
        a = Q[0, 0]
        b = Q[1, 1]
        return e.x_c[0], e.x_c[1], a, b, angle
    
    def createPatchesNeighborhood(self, indexTarget, indexSensor, color): 
        #type(e) = cvx.Ellipse
        e = self._neighborhoods[indexTarget, indexSensor]
    
        #Get center of ellipse(x0, y0), length of the bigger semiaxis - a,
        #the length of the smaller semiaxis - b, 
        #angle - the angle between the x-axis and the bigger semiaxis  
        x0, y0, a, b, angle = self.getDataPatchesEllipse(e)
        #print 'angle', np.degrees(angle), 'a,b', a, b
        pattern = patches.Ellipse((x0, y0), 2*a, 2*b, np.degrees(angle), edgecolor = color, fill=False)
        return pattern        
        
    def getIntersectionEllipses(self):
        self.outerEllipses = []
        numTargets = self.getNumTargets
        for i in range(numTargets):
            finalEllipse = cvx.findIntersection(self.neighborhoods[i, :])
            self.outerEllipses.append(finalEllipse)
    
    def createPathesIntersection(self, indexTarget, color):
        #type(e) = cvx.Ellipse
        e = self.outerEllipses[indexTarget]
        angle = -0.5 * np.arctan2(2*e.P[0][1], e.P[1][1]-e.P[0][0])
        #Clockwise rotation matrix
        R = np.array([[np.cos(angle), np.sin(angle)],
                      [-np.sin(angle), np.cos(angle)]])
        Q = np.dot(np.dot(R, e.P), np.transpose(R))
        x0, y0 = e.x_c
        pattern = patches.Ellipse((x0, y0), 2*Q[0, 0], 2*Q[1, 1],  np.degrees(angle),
                                  edgecolor = color, fill=False)
        return pattern 
        
    #outer boundary, result - square, create by cvxlib
    def createIntersectionBoundary2(self, indexTarget):
        #type(e) = cvx.Ellipse
        e = self.outerEllipses[indexTarget]
        angle = -0.5 * np.arctan2(2*e.P[0][1], e.P[1][1]-e.P[0][0])
        R = np.array([[np.cos(angle), np.sin(angle)],
                      [-np.sin(angle), np.cos(angle)]])
        Q = np.dot(np.dot(R, e.P), np.transpose(R))
        #find size of square side
        size = 2 * max(Q[0, 0], Q[1, 1])
        xCenter, yCenter = e.x_c
        return xCenter, yCenter, size
    
        
    #outer boundary, result - square, create by confidence ellipses
    def createIntersectionBoundary(self, indexTarget, indsSensors):
        minSize = float('inf')     
        for j in indsSensors:
            e = self.neighborhoods[indexTarget, j]
            angle = -0.5 * np.arctan2(2*e.P[0][1], e.P[1][1]-e.P[0][0])
            R = np.array([[np.cos(angle), np.sin(angle)],
                          [-np.sin(angle), np.cos(angle)]])
            Q = np.dot(np.dot(R, e.P), np.transpose(R))
            semiaxis = max(Q[0, 0], Q[1, 1])
            if minSize > semiaxis:
                minSize = semiaxis
                xCenter, yCenter = e.x_c
        return xCenter, yCenter, 2 * minSize
    
    def inEllipse(self, point, e):
        #type(e) = cvx.Ellipse
        #point.T = point        
        leftPart = np.dot(np.dot(point, e.A), point) + 2 * np.dot(point, e.b) + e.c 
        if leftPart <= 0:
            return True
        return False
    
    def methodMonteCarlo(self, indexTarget, indSensors):
        #find boundary
        x_c, y_c, size = self.createIntersectionBoundary(indexTarget, indSensors)
        #print 'xy', x_c, y_c, 'size = ', size
        boundaryVol = np.power(size, 2)
        numShots = 25 * boundaryVol
        
        a = np.random.uniform(x_c-size/2, x_c+size/2, numShots)
        b = np.random.uniform(y_c-size/2, y_c+size/2, numShots)
        
        counter = 0
        for x, y in zip(a, b):
            #count those points that belong to all ellipses at once
            if all(self.inEllipse(np.array([x, y]), self.neighborhoods[indexTarget, j]) for j in indSensors):
                counter += 1
        volume = float(counter) / float(numShots) * boundaryVol
        return volume

    def methodMonteCarloLMI(self, indexTarget, indSensors):
        #find boundary
        x_c, y_c, size = self.createIntersectionBoundary2(indexTarget)
        boundaryVol = np.power(size, 2)
        numShots = 25 * boundaryVol
        
        a = np.random.uniform(x_c-size/2, x_c+size/2, numShots)
        b = np.random.uniform(y_c-size/2, y_c+size/2, numShots)
        
        counter = 0
        for x, y in zip(a, b):
            #count those points that belong to all ellipses at once
            if all(self.inEllipse(np.array([x, y]), self.neighborhoods[indexTarget, j]) for j in indSensors):
                counter += 1
        volume = float(counter) / float(numShots) * boundaryVol
        return volume
        
    def solveByLMI(self, alpha):
        start_time = time.time()
        limit = 0.001
        resourceMatrix, self.outerEllipses = cvx.distributeSensors(self.neighborhoods, alpha)
        for i in range(resourceMatrix.shape[0]):
            for j in range(resourceMatrix.shape[1]):
                if resourceMatrix[i, j] > limit:
                    resourceMatrix[i, j] = 1
                else:
                    resourceMatrix[i, j] = 0
        
        numTargets = self.getNumTargets
        for i in range(numTargets):
            indsSensors =  np.asarray(np.where(resourceMatrix[i,:] == 1)[1]).reshape(-1)
            vol  = self.methodMonteCarloLMI(i, indsSensors)
            fq = vol + alpha * len(indsSensors)
        
        print 'timer LMI:', time.time() - start_time, 'seconds'
        #print 'resourceMatrix', resourceMatrix
        try:
            now = datetime.datetime.now()
            now = now.strftime("%Y-%m-%d %H-%M-%S")
            name = now.__str__() + ' LMI.txt'
            with open(name, "a+") as file_handler:
                numTargets = self.getNumTargets
                line = 'resource matrix = \n'
                line += resourceMatrix.__str__() + '\n'
                
                spaceTargetSec = 11
                bondaryBtm =  numTargets * spaceTargetSec * '-' + '\n'
                line += bondaryBtm
                line += '|target' + (spaceTargetSec * numTargets - 7) * ' ' +  '|Total volume\n'
                
                for l in range(numTargets):
                    line += '|' + l.__str__() + (spaceTargetSec - 1 - len(l.__str__())) * ' ' 
                line += '\n' + bondaryBtm
                
                summ = 0
                for i in range(numTargets):
                    vol = cvx.getEllipseVolume(self.outerEllipses[i])
                    summ += vol
                    volStr = '%0.4f' % vol
                    tempN = spaceTargetSec - 1 - len(volStr)
                    line += '|' + volStr + tempN * ' '
                line += '|' + '%0.4f' % summ + '\n' + bondaryBtm
                file_handler.writelines(line)
                
        except IOError:
            print("An IOError has occurred!")

#    def solveByLMI(self):
#        numSensors = self.getNumSensors
#        numTargets = self.getNumTargets
#        try:
#            now = datetime.datetime.now()
#            now = now.strftime("%Y-%m-%d %H-%M-%S")
#            name = now.__str__() + ' LMI.txt'
#            with open(name, "a+") as file_handler:
#                numSpaceSubsets = numSensors * 3 + 2                
#                line = 'subsets' + ' ' * max((numSpaceSubsets - 7), 0)
#                numSpaceSubsets = len(line)
#                
#                spaceTargetSec = 11
#                line += '|target' + (spaceTargetSec * numTargets - 7) * ' ' +  '|Total volume\n'
#                bondaryBtm = len(line) * '-' + '\n'        
#                line += bondaryBtm
#                
#                line += numSpaceSubsets * ' ' 
#                for l in range(numTargets):
#                    line += '|' + l.__str__() + (spaceTargetSec - 1 - len(l.__str__())) * ' ' 
#                line += '|\n'
#                line += bondaryBtm
#                file_handler.writelines(line)
#                #LMI___________________________________________________________
#                indsSensors = []
#                print indsSensors[:]
#                tempN = numSpaceSubsets - len(indsSensors[:].__str__()) 
#                line = indsSensors[:].__str__() + tempN * ' '
#                file_handler.write(line)
#                summ = 0
#                for i in range(numTargets):
#                    vol = self.methodMonteCarlo(i, indsSensors)
#                    summ += vol
#                    print 'target', i, ' vol = ', vol
#                    volStr = '%0.4f' % vol
#                    tempN = spaceTargetSec - 1 - len(volStr)
#                    line = '|' + volStr + tempN * ' '
#                    file_handler.write(line)
#                summStr = '%0.4f' % summ 
#                line = '|' +  summStr +'\n'
#                file_handler.write(line)
#                #end LMI_______________________________________________________
#        except IOError:
#            print("An IOError has occurred!")    

    def bruteForceT(self, alpha):
        start_time = time.time()
        print 'timer BF start:', datetime.datetime.now(), 'seconds'
        numSensors = self.getNumSensors
        numTargets = self.getNumTargets
#brute force___________________________________________________
        num = np.power(2, numSensors)
        for k in range(1, num):
            indsSensors = []
            for j in range(numSensors):
                if k & (1 << j):
                    indsSensors.append(j)
            summ = 0
            for i in range(numTargets):
                vol = self.methodMonteCarlo(i, indsSensors)
                fq = vol + alpha * len(indsSensors)
                summ += vol
 #end brute force_______________________________________________
        print 'timer BF:', time.time() - start_time, 'seconds'
        print 'timer end:', datetime.datetime.now()
        
        
    def bruteForce(self, alpha):
        numSensors = self.getNumSensors
        numTargets = self.getNumTargets
        try:
            now = datetime.datetime.now()
            now = now.strftime("%Y-%m-%d %H-%M-%S")
            name = now.__str__() + ' brute force.txt'
            with open(name, "a+") as file_handler:
                numSpaceSubsets = numSensors * 3 + 2                
                line = 'subsets' + ' ' * max((numSpaceSubsets - 7), 0)
                numSpaceSubsets = len(line)
                
                spaceTargetSec = 22
                line += '|target' + (spaceTargetSec * numTargets - 7) * ' ' +  '|Total volume\n'
                bondaryBtm = len(line) * '-' + '\n'        
                line += bondaryBtm
                
                line += numSpaceSubsets * ' ' 
                for l in range(numTargets):
                    line += '|' + l.__str__() + (spaceTargetSec - 1 - len(l.__str__())) *' ' 
                line += '|\n'
                line += bondaryBtm
                file_handler.writelines(line)
                #brute force___________________________________________________
                num = np.power(2, numSensors)
                for k in range(1, num):
                    indsSensors = []
                    for j in range(numSensors):
                        if k & (1 << j):
                            indsSensors.append(j)
                    print indsSensors[:]
                    tempN = numSpaceSubsets - len(indsSensors[:].__str__()) 
                    line = indsSensors[:].__str__() + tempN * ' '
                    file_handler.write(line)
                    summ = 0
                    for i in range(numTargets):
                        vol = self.methodMonteCarlo(i, indsSensors)
                        fq = vol + alpha * len(indsSensors)
                        summ += vol
                        print 'target', i, ' vol = ', vol
                        volStr = '%0.4f' % vol
                        fqStr = '%0.4f' % fq
                        tempN = spaceTargetSec / 2 - 1 - len(volStr)
                        line = '|' + volStr + tempN * ' '
                        tempN = spaceTargetSec / 2 - 1 - len(fqStr)
                        line += '|' + fqStr + tempN * ' '
                        file_handler.write(line)
                    summStr = '%0.4f' % summ 
                    line = '|' +  summStr +'\n'
                    file_handler.write(line)
                #end brute force_______________________________________________
        except IOError:
            print("An IOError has occurred!")    
                        
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
        
            
        
