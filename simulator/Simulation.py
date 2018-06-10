# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 13:55:02 2017

@author: scandaele
"""

import threading
import time
import json
import queue
from simulatorAPIClasses import simulatorAPI
import sys

# Thread to manage an offline simulation
class simulationOfflineThread(threading.Thread):

    def __init__(self, scenario, downQueue, upQueue, logFileLock, simuAPI, simulationQueue, eventSMQueue, eventLock, logFile = None):
        threading.Thread.__init__(self)
        self.eventSMQueue = eventSMQueue
        self.eventLock = eventLock
        self.scenario = scenario
        self.downQueue = downQueue
        self.upQueue = upQueue
        self.logFile = logFile
        self.logFileLock = logFileLock
        self.pauseSimulation = False
        self.simuAPI = simuAPI
        self.simulationQueue = simulationQueue
        
    def run(self):
        timeUnit = -1
        
        exitFlag = False
        endOfflineMsgSent = False

        OfflineTime = self.scenario.data['OfflineTime']

        totalPauseTime = 0.0
        
        startPause = 0
        endPause = 0

        # Wait for the solver to be connected before sending requests
        while not self.simuAPI.testConnection():
            time.sleep(1)

        # send all the offline requests of the scenario
        for request in self.scenario.data['Requests']:
            if request['RevealTime'] == -1:
                msg = json.dumps(request)
                msg = '{"NewRequests" : ' + msg + "}"
                self.simuAPI.sendNewRequestsJsonToSolver(msg)
                if self.logFile is not None:
                    self.logFileLock.acquire()
                    localtime = time.asctime( time.localtime(time.time()) )
                    lf = open(self.logFile, 'a')
                    lf.write(localtime + ' : ' + 'mesage to solver : \n' + msg + '\n\n')
                    lf.close()
                    self.logFileLock.release()
        
        # wait the solver to be ready for the simulation
        while not self.simuAPI.isReadyForOffline():
            pass

        print('   The solver is ready, offline simulation will start very shortly')

        # The simulator API decide the starTime, we wait until this time to start
        startTime = self.simuAPI.startOfflineSimulation();
        self.upQueue.put(('startTimeOffline', startTime))
        self.eventLock.acquire()
        self.eventSMQueue.set()
        self.eventLock.release()

        while not exitFlag:

            # check if solver confirm the pause
            while not self.simuAPI.pauseMessageQueue.empty():
                message = self.simuAPI.pauseMessageQueue.get()
                if message[0] == "OK":
                    self.simuAPI.pauseMessageThread.join()
                    self.simuAPI.pauseMessageThread = None
                    startPause = message[1]
                    endPause = sys.float_info.max
                    self.pauseSimulation = True
                    self.upQueue.put(('startOfflinePause',startPause))
                    self.eventLock.acquire()
                    self.eventSMQueue.set()
                    self.eventLock.release()
            

            while not self.downQueue.empty():
                message = self.downQueue.get()
                
                # order to start a pause
                if message == 'pause' :
                    self.simuAPI.sendPauseMessageT()
                
                # order to end a pause   
                elif message == 'continue':
                    if self.simuAPI.testConnection() == True:
                        if self.pauseSimulation == True:
                            endPause = self.simuAPI.sendContinueMessage()
                            totalPauseTime +=  endPause - startPause
                            self.upQueue.put(('endOfflinePause',endPause))
                            self.eventLock.acquire()
                            self.eventSMQueue.set()
                            self.eventLock.release()
                        else:
                            print('   Simulation not in pause')

                # send an empty solution to the solver
                elif message == 'sendEmptySolutionWithTOS':
                    self.simuAPI.setCurrentSolution(json.dumps('{"TimeOfSubmission":'+str(timeUnit)+'}'))

                # order to close the simulator
                elif message == 'close':
                    self.simuAPI.sendCloseMessage()
                    exitFlag = True

                # order to close the simulator
                elif message == 'stopSimulation':
                    self.simuAPI.sendCloseMessage()
                    exitFlag = True

                # simulation manager ask to close the thread
                elif message == 'closeThread':
                    exitFlag = True

                # if rpc error, end the simulation
                elif message == 'RpcError : close':
                    exitFlag = True
            
            while not self.simulationQueue.empty():
                message = self.simulationQueue.get()
                if message == 'sendTimeUnit':
                    tu = (time.time() - startTime - OfflineTime)
                    self.simuAPI.timeUnitQueue.put(tu/OfflineTime)

                elif message == 'close':
                    print('   SIMULATION OFFLINE THREAD :: close from simulationQueue')
                    exitFlag = True

                elif message.startswith("logFile "):
                    self.logFile = message.replace('logFile ', '', 1)
            
            # check if we reach the end of the offline time
            if ( time.time() - startTime - totalPauseTime ) >= OfflineTime:
                if not self.pauseSimulation and not endOfflineMsgSent:
                    endOfflineMsgSent = True
                    self.upQueue.put(('endOfOfflineSimulation',))
                    self.eventLock.acquire()
                    self.eventSMQueue.set()
                    self.eventLock.release()

            elif time.time() > endPause:
                self.pauseSimulation = False

                
                            
class simulationOnlineThread(threading.Thread):
    
    def __init__(self, scenario, downQueue, upQueue, horizonSize, logFileLock, simuAPI, simulationQueue, eventSMQueue, eventLock, logFile = None):
        threading.Thread.__init__(self)
        self.eventSMQueue = eventSMQueue
        self.eventLock = eventLock
        self.scenario = scenario
        self.horizonSize = horizonSize
        self.downQueue = downQueue
        self.upQueue = upQueue
        self.logFile = logFile
        self.logFileLock = logFileLock
        self.pauseSimulation = False
        self.simuAPI = simuAPI
        self.simulationQueue = simulationQueue
        #security margin, so that requests are available for solver at the beginning of the time unit
        self.marginTimeRequestSending = 0.2
        
    def run(self):
        timeUnit = 0
        
        exitFlag = False
        ComputationTime = self.scenario.data['ComputationTime']

        totalPauseTime = 0.0
        
        startPause = 0
        endPause = 0


        numberRequestToSend = 0
        # count the number of request to send at the first time unit
        for request in self.scenario.data['Requests']:
            if request['RevealTime'] == 0:
                numberRequestToSend += 1

        while not self.simuAPI.isReadyForOnline():
            pass

        print('   The solver is ready, online simulation will start very shortly')

        # The simulator API decide the starTime, we wait until this time to start
        startTime = self.simuAPI.startOnlineSimulation()
        self.upQueue.put(('startTimeOnline', startTime))
        self.eventLock.acquire()
        self.eventSMQueue.set()
        self.eventLock.release()

        while not exitFlag:

            while not self.simuAPI.pauseMessageQueue.empty():
                message = self.simuAPI.pauseMessageQueue.get()
                if message[0] == "OK":
                    self.simuAPI.pauseMessageThread.join()
                    self.simuAPI.pauseMessageThread = None
                    endPause = sys.float_info.max
                    startPause = message[1]
                    self.pauseSimulation = True
                    self.upQueue.put(('startOnlinePause',startPause))
                    self.eventLock.acquire()
                    self.eventSMQueue.set()
                    self.eventLock.release()
            
            while not self.downQueue.empty():
                message = self.downQueue.get()
                
                if message == 'pause' :
                    self.simuAPI.sendPauseMessageT()
                    
                elif message == 'continue':
                    if self.simuAPI.testConnection() == True:
                        if self.pauseSimulation == True:
                            endPause = self.simuAPI.sendContinueMessage()
                            totalPauseTime +=  endPause - startPause
                            self.upQueue.put(('endOnlinePause',endPause))
                            self.eventLock.acquire()
                            self.eventSMQueue.set()
                            self.eventLock.release()
                        else:
                            print('   Simulation not in pause')

                    
                elif message.startswith('newRequest'):
                    # The simulation manager thread communicate a new Request
                    # except the TU, the validity was already verified
                    newRequest = json.loads(message.replace('newRequest ', ''))

                    # Request with a RevealTime anterior to the current Time are not inserted
                    if newRequest['RevealTime'] >= timeUnit:
                        self.upQueue.put((message,))
                        self.eventLock.acquire()
                        self.eventSMQueue.set()
                        self.eventLock.release()




                elif message == 'sendEmptySolutionWithTOS':
                    self.simuAPI.setCurrentSolution(json.dumps('{"TimeOfSubmission":'+str(timeUnit)+'}'))

                elif message == 'close':
                    self.simuAPI.sendCloseMessage()
                    exitFlag = True

                # order to close the simulator
                elif message == 'stopSimulation':
                    self.simuAPI.sendCloseMessage()
                    exitFlag = True

                # simulation manager ask to close the thread
                elif message == 'closeThread':
                    exitFlag = True

                elif message == 'RpcError : close':
                    exitFlag = True
            
            while not self.simulationQueue.empty():
                message = self.simulationQueue.get()
                if message == 'sendTimeUnit':
                    tu = (time.time() - startTime)
                    if tu >= 0:
                        self.simuAPI.timeUnitQueue.put(tu/ComputationTime)
                    else :
                        print('   ERROR: should not have negative time unit in online simulation')

                elif message == 'close':
                    exitFlag = True

                elif message.startswith("logFile "):
                    self.logFile = message.replace('logFile ', '', 1)
            
            # test the beginning of a new time unit
            if (time.time() - startTime - totalPauseTime) >= timeUnit * ComputationTime - self.marginTimeRequestSending * numberRequestToSend :
                
                if not self.pauseSimulation:
                    numberRequestToSend = 0
                    endPause = 0
                    startPause = 0

                    self.upQueue.put(('newTimeUnit', timeUnit))
                    self.eventLock.acquire()
                    self.eventSMQueue.set()
                    self.eventLock.release()

                    for request in self.scenario.data['Requests']:
                        if request['RevealTime'] > timeUnit+1:
                            pass
                        if request['RevealTime'] == timeUnit + 1:
                            numberRequestToSend += 0.5
                        if request['RevealTime'] == timeUnit:
                            msg = json.dumps(request)
                            msg = '{"NewRequests" : ' + msg + "}"
                            self.simuAPI.sendNewRequestsJsonToSolver(msg)
                            if self.logFile is not None:
                                self.logFileLock.acquire()
                                localtime = time.asctime( time.localtime(time.time()) )
                                lf = open(self.logFile, 'a')
                                lf.write(localtime + ' : ' + 'mesage to solver : \n' + msg + '\n\n')
                                lf.close()
                                self.logFileLock.release()

                    timeUnit += 1
                    if timeUnit >= self.horizonSize:  
                        self.upQueue.put(('endOfOnlineSimulation',  (time.time() - startTime - totalPauseTime)/ComputationTime))
                        self.eventLock.acquire()
                        self.eventSMQueue.set()
                        self.eventLock.release()
                    
                    

                self.simuAPI.testConnection()

            elif time.time() > endPause:
                self.pauseSimulation = False  
