# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 15:29:39 2017

@author: simon
"""

from __future__ import print_function
from concurrent import futures

import grpc
import json
import time
import threading
import queue
import os

import vrpAPI_pb2
import vrpAPI_pb2_grpc

class simulatorAPI:
    def __init__(self, pauseMessageQueue, upQueue, eventSMQueue, eventLock):
        self.pauseMessageQueue = pauseMessageQueue
        self.upQueue = upQueue
        self.eventSMQueue = eventSMQueue
        self.eventLock = eventLock
        self.pauseMessageThread = None
        self.solverPort = -1
        self.channel = grpc.insecure_channel('localhost:' + self.getSolverPort()) 
        self.stub = vrpAPI_pb2_grpc.SimulatorMessagesStub(self.channel)

    def handleGrpcError(self, error, message):
        print(message)
        print(error.details())
        self.upQueue.put('RpcError : Connect Failed')
        self.eventLock.acquire()
        self.eventSMQueue.set()
        self.eventLock.release()

    def getSolverPort(self):
        if self.solverPort is -1:
            configPath = os.path.join(os.path.dirname(__file__), '../Config/config.txt')
            with open(configPath, 'r') as configFile:
                line = configFile.readline()
                while line:
                    if line.startswith("SolverPort ="):
                        line = line.replace("SolverPort =", "")
                        self.solverPort = int(line)
                    else:
                        line = configFile.readline()
        return str(self.solverPort)

    def isReady(self):
        try:
            response = self.stub.isReady(vrpAPI_pb2.Empty()) 
            return response.b 
        except grpc.RpcError as e:
            self.handleGrpcError(e, 'Error with function isReady() from simulatorAPI')

    def isReadyForOffline(self):
        try:
            response = self.stub.isReadyForOffline(vrpAPI_pb2.Empty())
            return response.b
        except grpc.RpcError as e:
            self.handleGrpcError(e, 'Error with function isReadyForOffline() from simulatorAPI')

    def isReadyForOnline(self):
        try:
            response = self.stub.isReadyForOnline(vrpAPI_pb2.Empty())
            return response.b
        except grpc.RpcError as e:
            self.handleGrpcError(e, 'Error with function isReadyForOnline() from simulatorAPI')

    def sendGraphJsonToSolver(self, graphJson):
        try:
            msg = '{"Graph": ' + graphJson + '}'
            self.stub.loadJson(vrpAPI_pb2.JsonMessage(jsonstring=msg))
        except grpc.RpcError as e:
            self.handleGrpcError(e, 'Error when sending graphJson to solver')
      
    def sendCarrierJsonToSolver(self, carrierJson):
        try:
            msg = '{"Carrier": ' + carrierJson + '}'
            self.stub.loadJson(vrpAPI_pb2.JsonMessage(jsonstring=msg))
        except grpc.RpcError as e:
            self.handleGrpcError(e, 'Error when sending carrierJson to solver')
            
    def sendCustomersJsonToSolver(self, customersJson):
        try:
            msg = '{"Customers": ' + customersJson + '}'
            self.stub.loadJson(vrpAPI_pb2.JsonMessage(jsonstring=msg))
        except grpc.RpcError as e:
            self.handleGrpcError(e, 'Error when sending customersJson to solver')
      
    def sendNewRequestsJsonToSolver(self, newRequests):
        try:
            self.stub.loadJson(vrpAPI_pb2.JsonMessage(jsonstring=newRequests))
        except grpc.RpcError as e:
            self.handleGrpcError(e, 'Error when sending newRequests to solver')
      
    def sendCurrentTimeUnit(self, timeUnit):
        try:
            self.stub.currentTimeUnit(vrpAPI_pb2.TimeUnitMessage(timeunit=timeUnit))
        except grpc.RpcError as e:
            self.handleGrpcError(e, 'Error when sending CurrentTimeUnit to solver')

    def sendPauseMessageT(self):
        if self.pauseMessageThread is None:
            self.pauseMessageThread = SendPauseMessageThread(self.pauseMessageQueue, self.stub)
            self.pauseMessageThread.start()
        else:
            print("Previous pause command not fihished")

      
    def sendContinueMessage(self):
        try:
            reply = self.stub.continueSimulation(vrpAPI_pb2.Empty()) 
            return reply.value 
        except grpc.RpcError as e:
            self.handleGrpcError(e, 'Error when sending continueMessage to solver')
            
    def sendCloseMessage(self):
        try:
            self.stub.shutdown(vrpAPI_pb2.Empty())  
        except grpc.RpcError as e:
            self.handleGrpcError(e, 'Error when sending closeMessage to solver')

    def sendFile(self, jsonMsg):
        try:
            self.stub.loadJson(vrpAPI_pb2.JsonMessage(jsonstring=jsonMsg))
        except grpc.RpcError as e:
            self.handleGrpcError(e, 'Error when sending newRequests to solver')

    def setCurrentSolution(self, jsonMsg):
        try:
            self.stub.setCurrentSolution(vrpAPI_pb2.JsonMessage(jsonstring=jsonMsg))
        except grpc.RpcError as e:
            self.handleGrpcError(e, 'Error when sending currentSolution to solver')

    def startSimulation(self):
        try:
            reply = self.stub.startSimulation(vrpAPI_pb2.Empty())
            return reply.value  
        except grpc.RpcError as e:
            self.handleGrpcError(e, 'Error when sending startSimulation to solver')

    def startOfflineSimulation(self):
        try:
            reply = self.stub.startOfflineSimulation(vrpAPI_pb2.Empty())
            return reply.value  
        except grpc.RpcError as e:
            self.handleGrpcError(e, 'Error when sending startSimulation to solver')

    def startOnlineSimulation(self):
        try:
            reply = self.stub.startOnlineSimulation(vrpAPI_pb2.Empty())
            return reply.value  
        except grpc.RpcError as e:
            self.handleGrpcError(e, 'Error when sending startSimulation to solver')

    def testConnection(self):
        try:
            self.stub.testConnection(vrpAPI_pb2.Empty())
            return True
        except grpc.RpcError as e:
            self.handleGrpcError(e, 'Error when testing the connection')
            return False
    
 
    
class SolverMessagesImpl(vrpAPI_pb2_grpc.SolverMessagesServicer):
    def __init__(self, simulationQueue, solutionsQueue, timeUnitQueue, eventSMQueue, eventLock):
        self.simulationQueue = simulationQueue
        self.solutionsQueue = solutionsQueue
        self.timeUnitQueue = timeUnitQueue
        self.eventSMQueue = eventSMQueue
        self.eventLock = eventLock

    def acceptRequest(self, request, context):
        jsonMsg = request.jsonstring
        self.eventLock.acquire()
        self.solutionsQueue.put(('acceptedRequest', jsonMsg))
        self.eventSMQueue.set()
        self.eventLock.release()



    def notifyEndOffline(self, request, context):
        self.eventLock.acquire()
        self.solutionsQueue.put(("SolverEndOffline",))
        self.eventSMQueue.set()
        self.eventLock.release()
        return vrpAPI_pb2.Empty()

    def notifyEndOnline(self, request, context):
        self.eventLock.acquire()
        self.solutionsQueue.put(("SolverEndOnline",))
        self.eventSMQueue.set()
        self.eventLock.release()
        return vrpAPI_pb2.Empty()
    
    def sendBestSolution(self, request, context):
        # correct the instance returned by the initial solver of michael
        # solverSol = json.loads(request.jsonstring)
        # for road in solverSol['Routes']:
        #     for node in solverSol['Routes'][road]:
        #         if 'InstanceVertexID' in node:
        #             node['RequestId'] = node['InstanceVertexID']
        #             del(node['InstanceVertexID'])
        #         if 'RequestInstanceId' in node:
        #             node['Node'] = node['RequestInstanceId']
        #             del(node['RequestInstanceId'])

        # send the sol to SimulationManager
        self.solutionsQueue.put(('updateBestSolution',request.jsonstring))
        #self.solutionsQueue.put(('updateBestSolution', json.dumps(solverSol)))
        self.eventLock.acquire()
        self.eventSMQueue.set()
        self.eventLock.release()
        return vrpAPI_pb2.Empty()

    def testConnection(self, request, context):
        return vrpAPI_pb2.Empty()

    def getTimeUnit(self, request, context):
        self.simulationQueue.put("sendTimeUnit")
        while self.timeUnitQueue.empty():
            pass
        tu = self.timeUnitQueue.get()
        return vrpAPI_pb2.TimeUnitMessage(timeunit = tu)



class SolverListenerThread(threading.Thread):
    def __init__(self, queue, simulationQueue, solutionsQueue, timeUnitQueue, eventSMQueue, eventLock):
        threading.Thread.__init__(self)
        self.queue = queue
        self.simulationQueue = simulationQueue
        self.solutionsQueue = solutionsQueue
        self.timeUnitQueue = timeUnitQueue
        self.eventSMQueue = eventSMQueue
        self.eventLock = eventLock
    
    def run(self):
        listenerPort = -1
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        vrpAPI_pb2_grpc.add_SolverMessagesServicer_to_server(SolverMessagesImpl(self.simulationQueue, self.solutionsQueue, self.timeUnitQueue, self.eventSMQueue, self.eventLock), server)
        configPath = os.path.join(os.path.dirname(__file__), '../Config/config.txt')
        with open(configPath, 'r') as configFile:
            # loop to find the port in the config file
            line = configFile.readline()
            while listenerPort is -1:
                if line.startswith("SimulatorPort ="):
                    line = line.replace("SimulatorPort =", "")
                    line = line.replace("\n", "")
                    listenerPort = int(line)
                else:
                    line = configFile.readline()

        portAdded = server.add_insecure_port('localhost:' + str(listenerPort))
        if portAdded == listenerPort :
            server.start()
            keepLooping = True
            try:
                while keepLooping:
                    if not self.queue.empty():
                        msg = self.queue.get()
                        if msg == 'close':
                            keepLooping = False
                            server.stop(0)
                    time.sleep(1.5)
            except KeyboardInterrupt:
                server.stop(0)
        else:
            print("Error with the port of the simulator")

class SendPauseMessageThread(threading.Thread):
    # Thread to send the pause message and not be blocked by timeout
    def __init__(self, pauseMessageQueue, stub):
        threading.Thread.__init__(self)
        self.pauseMessageQueue = pauseMessageQueue
        self.stub = stub

    def run(self):
        try:
            reply = self.stub.pauseSimulation(vrpAPI_pb2.Empty()) #, timeout = 2)
            self.pauseMessageQueue.put(("OK", reply.value))
        except grpc.RpcError as e:
            self.handleGrpcError(e, '')
            if e.details() == "Deadline Exceeded":
                # the solver didn't answers
                self.pauseMessageQueue.put(("KO", None)) 
            else:
                print("Error when sending pauseMessage to solver")
                print(e.details())
