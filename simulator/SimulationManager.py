#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 13:48:53 2017

@author: simon
"""

import queue
import threading
from ScenarioClass import Scenario
from GraphClass import Graph
from CustomerClass import Customer
from CarrierClass import Carrier
import Simulation
from SolutionClass import Solution
import json
from pprint import pprint
from simulatorAPIClasses import SolverListenerThread
from simulatorAPIClasses import simulatorAPI
import time
import sys
import os

import argparse


class SMthread(threading.Thread):
    def __init__(self, commandQueue, eventCommand, eventSMQueue, eventLock):
        threading.Thread.__init__(self)
        self.eventCommand = eventCommand
        self.eventSMQueue = eventSMQueue
        self.eventLock = eventLock
        self.commandQueue = commandQueue
        self.dataNotSent = []
        self.dataSent = []
        self.logFile = None
        self.logFileLock = threading.Lock()
        self.mySolverListener = None
        self.downQueue = queue.Queue(50)
        self.upQueue = queue.Queue(50)
        self.guiQueue = None
        self.listenerQueue = queue.Queue(3)
        self.pauseMessageQueue = queue.Queue(10)
        self.simulationQueue = queue.Queue(10)
        self.simulationStatus = 'PreSimulation'
        self.solverStatus = 'PreSimulation'
        self.solutionsQueue = queue.Queue(10)
        self.timeUnitQueue = queue.Queue(10)
        self.simuAPI = simulatorAPI(self.pauseMessageQueue, self.upQueue, self.eventSMQueue, self.eventLock)

        self.eventCommandFinished = None
        self.scriptMode = False


    def setEventCommandFinished(self, eventCommandFinished):
        self.eventCommandFinished = eventCommandFinished

    def setScriptMode(self, param):
        self.scriptMode = param

    def setGuiQueue(self, guiQueue):
        self.guiQueue = guiQueue

    def sendToGUI(self, guiMessage):
        '''If the simulator is in GUI mode, send a message to the gui '''
        if self.guiQueue != None:
            self.guiQueue.put(guiMessage)

    def printLog(self, msg):
        if self.logFile is not None:
            self.logFileLock.acquire()
            localtime = time.asctime( time.localtime(time.time()) )
            lf = open(self.logFile, 'a')
            lf.write(localtime + ' : ' + str(msg) + ' \n\n')
            lf.close()
            self.logFileLock.release()

    def addToDataNotSent(self, msg):
        if msg not in self.dataNotSent:
            self.dataNotSent += [msg]

    def addToDataSent(self, msg):
        if msg not in self.dataSent:
            self.dataSent += [msg]

    def removeFromDataNotSent(self, msg):
        if msg in self.dataNotSent:
            self.dataNotSent.remove(msg)

    def removeFromDataSent(self, msg):
        if msg in self.dataSent:
            self.dataSent.remove(msg)

    def changeStatusTo(self, newStatus):
        self.simulationStatus = newStatus
        self.sendToGUI(('updateStatus', newStatus))

    def stopSimulation(self, mySolutions, mySimulation):
        """
            stop the simulation and reset the solutions
            join the thread mySimulation if necessary
        """
        returnValue = True
        if self.simulationStatus in ['OfflinePause']:
            # solver must end his pause to receive the stopsimulation message
            self.downQueue.put('continue')
            self.changeStatusTo('OfflineComputation')

        elif self.simulationStatus in ['OnlinePause']:
            # solver must end his pause to receive the stopsimulation message
            self.downQueue.put('continue')
            self.changeStatusTo('OnlineComputation')

        if self.simulationStatus in ['OfflinePauseAsked', 'OnlinePauseAsked']:
            returnValue = False

        elif self.simulationStatus in ['OfflineComputation', 'OnlineComputation']:
            self.downQueue.put('stopSimulation')
            mySimulation.join()
            for data in self.dataSent:
                self.addToDataNotSent(data)

            self.dataSent = []
            self.printLog('User command : stopSimulation')
            self.mySolutions = Solution()
            self.changeStatusTo('PreSimulation')
            self.solverStatus = 'PreSimulation'

        elif self.simulationStatus in ['OfflineEnd']:

            self.simuAPI.sendCloseMessage()
            for data in self.dataSent:
                self.addToDataNotSent(data)
            self.dataSent = []
            self.printLog('User command : stopSimulation')
            self.mySolutions = Solution()
            self.changeStatusTo('PreSimulation')
            self.solverStatus = 'PreSimulation'

        elif self.simulationStatus in ['PostSimulation']:
            for data in self.dataSent:
                self.addToDataNotSent(data)

            self.dataSent = []
            self.printLog('User command : stopSimulation')
            self.mySolutions = Solution()
            self.changeStatusTo('PreSimulation')
            self.solverStatus = 'PreSimulation'

        elif self.simulationStatus in ['PreSimulation']:
            for data in self.dataSent:
                self.addToDataNotSent(data)
            self.dataSent = []
            self.printLog('User command : stopSimulation')
            self.mySolutions = Solution()
            self.changeStatusTo('PreSimulation')
            self.solverStatus = 'PreSimulation'
        numberValid   = len(self.mySolutions.data['Solutions'])
        numberInvalid = len(self.mySolutions.data['SolutionsNotValid'])
        return returnValue

    def run(self):
        verbose = False

        exitFlag = simulationStarted = False
        runningSimulation = False
        mySimulation = None
        pauseAsked = False
        myCarrier = Carrier()
        myScenario = Scenario()
        myGraph = Graph()
        myCustomer = Customer()
        myFiles = {}
        self.mySolutions = Solution()
        self.mySolverListener = SolverListenerThread(self.listenerQueue, self.simulationQueue, self.solutionsQueue, self.timeUnitQueue, self.eventSMQueue, self.eventLock)
        self.mySolverListener.start()

        testParser = argparse.ArgumentParser(prog = 'test',)
        testParser.add_argument('--ct', type=float, default=argparse.SUPPRESS)
        testParser.add_argument('--ot', type=float, default=argparse.SUPPRESS)
        testParser.add_argument('--path', nargs = '+', default=argparse.SUPPRESS)

        gsParser = argparse.ArgumentParser(prog = 'generateScenario', usage = None, add_help=True, description = 'generate a scenario from the customer file loaded')
        gsParser.add_argument('--ct', type=float, default=5.0, help = 'computation time for each time unit')
        gsParser.add_argument('--ot', type=float, default=0.0, help = 'computation time for the offline requests')


        while not exitFlag:
            # wait for a event to manage
            self.eventSMQueue.wait()

            if verbose:
                print('   SimulationManager :: command receive')


            self.eventLock.acquire()
            self.eventSMQueue.clear()
            self.eventLock.release()

            while not self.commandQueue.empty():
                command = self.commandQueue.get()
                commandSplit = command.split()

                if len(commandSplit) == 0:
                    pass
                elif commandSplit[0] == 'addVehicles':
                    if self.simulationStatus != 'PreSimulation':
                        print('   Error: The fleet of vehicles can be modified only before the simulation')
                    else:
                        if not myCarrier.data:
                            print('   Error: No Carrier file is loaded')
                        else:
                            validArgs = True
                            if len(commandSplit) is 1:
                                validArgs = False
                                print('   Error: missing numbers and types of vehicles to be added')
                                self.printLog('User command: ' + command + ' : Error: missing numbers and types of vehicles to be added')
                            
                            elif len(commandSplit)%2 is 0:
                                validArgs = False
                                print('   Error: the number of argument is not correct')
                                self.printLog('User command: ' + command + ' Error: the number of argument is not correct')
                            
                            elif len(commandSplit)%2 is 1:
                                expect = 'Number'
                                for arg in commandSplit[1:]:
                                    if expect == 'Number':
                                        if not arg.isdigit():
                                            validArgs = False
                                            print('   Error: '+arg+' is not a number')
                                        expect = 'VehicleType'
                                    elif expect == 'VehicleType':
                                        if not myCarrier.containVehicleType(arg):
                                            validArgs = False
                                            print('   Error: '+arg+' is not a vehicle type in the carrier file')
                                        expect = 'Number'
                        
                            if validArgs:
                                # iterate on the number on the command
                                cs = commandSplit
                                noError = True
                                for num in range(1, len(cs), 2):
                                    if not str.isdigit(cs[num]):
                                        noError = False
                                        print('   Error: invalid argument : '+cs[num]+' should be a number')
                                        self.printLog('User command :'+command+' : Error: invalid argument : '+cs[num]+' should be a number')
                                    
                                    # check if vehicle type is in the available vehicle types
                                    if cs[num+1] not in [k['VehicleType'] for k in myCarrier.data['VehicleTypes']]:
                                        noError = False
                                        print('   Error: invalid argument : "'+cs+'" is not an available type of vehicle')
                                        self.printLog('User command : '+command+' : Error: invalid argument : "'+cs+'" is not an available type of vehicle')

                                if noError:
                                    # loop to add the vehicles
                                    maxId = -1
                                    if not not myCarrier.data['Vehicles']:
                                        maxId = max([int(vehicle) for vehicle in myCarrier.data['Vehicles']])
                                    for num in range(1, len(cs), 2):
                                        for i in range(0, int(cs[num])):
                                            maxId += 1
                                            newVehicle = {'VehicleType': cs[num+1]}
                                            myCarrier.data['Vehicles'][str(maxId)] = newVehicle
                                    self.sendToGUI(('carrierData', myCarrier.data))
                                    self.addToDataNotSent('Carrier')
                                    self.removeFromDataSent('Carrier')
                                    self.printLog('User command :' + command)
                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()



                elif commandSplit == ['data']:
                    print('   dataSent      : ', self.dataSent)
                    print('   data not sent :', self.dataNotSent)

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()

                elif commandSplit == ['close']:
                    # if simulationStarted: 
                    #     if mySimulation.pauseSimulation:
                    #         self.downQueue.put('continue')
                    # self.downQueue.put('close')
                    # self.listenerQueue.put('close')
                    # exitFlag = True
                    # self.printLog('User command : close')
                    if self.simulationStatus in ['OfflinePause', 'OnlinePause']:
                        self.downQueue.put('continue')
                    self.downQueue.put('close')
                    self.listenerQueue.put('close')
                    exitFlag = True
                    self.printLog('User command : close')

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()

                elif commandSplit == ['computationTime']:
                    if 'ComputationTime' not in myFiles or myFiles['ComputationTime'] == None:
                        print('The computation time is not defined\nUse command "setComputationTime" to set the computation time')
                    else:
                        print('ComputationTime set to {} seconds'.format(myFiles['ComputationTime']))
                    self.eventCommand.set()



                elif commandSplit == ['continue']:
                    # if not runningSimulation:
                    #     print('   No simulation is running')
                    # elif pauseAsked == False:
                    #     print('   The simulation is not in pause')
                    # else:
                    #     self.downQueue.put('continue')
                    #     pauseAsked = False
                    #     self.printLog('User command : continue')

                    if self.simulationStatus in ['OfflinePause', 'OnlinePause']:
                        self.downQueue.put('continue')
                        self.printLog('User command : continue')
                    elif self.simulationStatus in ['OfflineComputation', 'OnlineComputation']:
                        print('   ERROR: simulation not in pause')
                    elif self.simulationStatus in ['OfflinePauseAsked', 'OnlinePauseAsked']:
                        print('   ERROR: a precedent pause command was entered, the solver did not start the pause yet')
                    elif self.simulationStatus in ['PreSimulation', 'OfflineEnd', 'PostSimulation']:
                        print('   ERROR: there is currently no computation')

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()


                elif commandSplit == ['currentStatus']:
                    print('   Current status of the simulator : ',self.simulationStatus)
                    self.eventCommand.set()

                elif commandSplit == ['createNewSolution']:
                    self.mySolutions.newUserSolution()
                    self.eventCommand.set()

                elif commandSplit[0] == 'deleteRequest':
                    if len(commandSplit) != 3:
                        print('   incorrect number of arguments')
                    else:
                        requestId = commandSplit[1]
                        roadId = commandSplit[2]
                        if not self.mySolutions.deleteRequest(requestId, roadId):
                            print('   road '+roadId+' has no request '+requestId)

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()

                elif commandSplit == ['deleteVehicles']:
                    if self.simulationStatus in ['PreSimulation']:
                        myCarrier.data['Vehicles'] = {}
                        self.addToDataNotSent('Carrier')
                        self.removeFromDataSent('Carrier')
                        self.sendToGUI(('carrierData', myCarrier.data))
                    else:
                        print('   ERROR: the vehicle fleet can only be changed before the simulation')

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()

                elif commandSplit[0] == 'generateScenario':
                    if self.simulationStatus in ['PreSimulation']:
                        if not myCustomer.data:
                            print('      please load a Customer file in order to generate a scenario')
                            self.printLog('User command : generateScenario : ERROR no Customer file loaded')
                        else:
                            try:
                                args = gsParser.parse_args(command.replace('generateScenario', '', 1).split())
                                myScenario.generateScenario(myCustomer, args.ct, args.ot)
                                myFiles["ComputationTime"] = args.ct
                                myFiles["OfflineTime"] = args.ot
                                self.addToDataNotSent('ComputationTime')
                                self.addToDataNotSent('OfflineTime')
                                self.removeFromDataSent('ComputationTime')
                                self.removeFromDataSent('OfflineTime')
                                self.printLog('User command : generateScenario') 
                            except SystemExit:
                                self.printLog('User command : generateScenario : ERROR invalid options') 
                    else:
                        print('   ERROR: a scenario can only be generated before starting a simulation')

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()


                elif commandSplit[0] == 'insertRequest':
                    if len(commandSplit) != 4:
                        print('   Incorrect number of arguments (requestId and roadId and position)')
                    else:
                        requestId = commandSplit[1]
                        roadId = commandSplit[2]
                        position = commandSplit[3]
                        self.mySolutions.insertRequest(requestId, roadId, position, myGraph, myCarrier, myCustomer, myScenario)

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()

                elif commandSplit[0] == 'loadCarrier':
                    if self.simulationStatus in ['PreSimulation']:
                        command = command.replace('loadCarrier ', '', 1).rstrip()
                        if myCarrier.loadFile(command):
                            self.addToDataNotSent('Carrier')
                            self.removeFromDataSent('Carrier')
                            self.sendToGUI(('carrierData', myCarrier.data))
                        else:
                            self.sendToGUI(('error', 'Impossible to load this carrier file'))
                        self.printLog('User command : loadCarrier %s' % command)
                    else:
                        print('   ERROR: the carrier file can only be loaded before the simulation')

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()

                elif commandSplit[0] == 'loadCustomer':
                    if self.simulationStatus in ['PreSimulation']:
                        command = command.replace('loadCustomer ', '', 1).rstrip()
                        if myCustomer.loadFile(command):
                            self.addToDataNotSent('Customer')
                            self.removeFromDataSent('Customer')
                            self.sendToGUI(('customerData', myCustomer.data))
                        else:
                            self.sendToGUI(('error', 'Impossible to load this customer file'))
                        self.printLog('User command : loadCustomer %s' % command)
                    else:
                        print('   ERROR: the customer file can only be loaded before the simulation')

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()


                elif commandSplit[0] == 'loadFile':
                    if self.simulationStatus in ['PreSimulation']:
                        command = command.replace('loadFile', '', 1).split()
                        key = command[-1]
                        fileName = ' '.join(command[:len(command)-1])
                        try:
                            myFiles[key] = json.load(open(fileName))
                            self.addToDataNotSent('myFiles')
                            self.removeFromDataSent('myFiles')
                            self.printLog('User command : loadFile %s %s' % (str(fileName), str(key)))
                        except IOError:
                            print('   Error: cannot load the file', fileName) 
                            self.printLog('User command : loadFile %s %s \n Error: cannot send the file %s' % (str(fileName), str(key), str(fileName)))
                    else:
                        print('   ERROR: a data file can only be loaded before the simulation')

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()

                elif commandSplit[0] == 'loadGraph':
                    if self.simulationStatus in ['PreSimulation']:
                        command = command.replace('loadGraph ', '', 1).rstrip()
                        if myGraph.loadFile(command):
                            self.addToDataNotSent('Graph')
                            self.removeFromDataSent('Graph')
                            self.sendToGUI(('graphData', myGraph.data))
                        else:
                            self.sendToGUI(('error', 'Impossible to load this graph file'))
                        self.printLog('User command : loadGraph %s' % command)
                    else:
                        print('   ERROR: the graph file can only be loaded before the simulation')

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()

                       
                elif commandSplit[0] == 'loadScenario':
                    if self.simulationStatus in ['PreSimulation']:
                        command = command.replace('loadScenario ', '', 1).rstrip()
                        if myScenario.loadFile(command):
                            if 'ComputationTime' not in myScenario.data and 'ComputationTime' in myFiles:
                                del(myFiles["ComputationTime"])
                                self.addToDataNotSent('ComputationTime')
                                self.removeFromDataSent('ComputationTime')
                            if 'OfflineTime' not in myScenario.data and 'OfflineTime' in myFiles:
                                del(myFiles["OfflineTime"])
                                self.addToDataNotSent('OfflineTime')
                                self.removeFromDataSent('OfflineTime')
                            self.sendToGUI(('scenarioData', myScenario.data))
                        else:
                            self.sendToGUI(('error', 'Impossible to load this scenario file'))
                        self.printLog('User command : loadScenario %s' % command)
                    else:
                        print('   ERROR: the scenario file can only be loaded before the simulation')

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()



                elif commandSplit[0] == 'loadNewSolution':
                    # commande pour charger une nouvelle solution que le solveur doit utiliser
                    if self.simulationStatus in ['OfflineComputation', 'OfflinePause','OfflineEnd', 'OnlineComputation', 'OnlinePause']:
                        command = command.replace('loadSolutions ', '', 1).rstrip()
                        solution = self.mySolutions.loadFileSolverSol(commandSplit[1], myGraph, myCarrier, myScenario, myCustomer.data["TimeSlots"])
                        if solution == False:
                            print('   ERROR: the solution is invalid')
                            self.sendToGUI(('error', 'The solution in the file is invalid'))
                        else:
                            print('   New solution load')
                            solution['TimeUnitOfSubmission'] = 0
                            self.simuAPI.setCurrentSolution(json.dumps(solution))
                            self.sendToGUI(('newSolutionLoaded', solution))

                        self.printLog('User command : loadSolution %s' % command)

                        if verbose:
                            print('   SimulationManager :: serve command :: ', command)
                    else:
                        print('   this command can currently be used only after the offline Time and before the online time ')
                    self.eventCommand.set()

                elif commandSplit[0] == 'loadUserSolutions':
                    command = command.replace('loadSolutions ', '', 1).rstrip()
                    self.mySolutions.loadFile(command)
                    self.printLog('User command : loadSolution %s' % command)

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()

                elif commandSplit[0] == 'newRequest':
                    if self.simulationStatus not in ['PostSimulation']:
                        # load the request and check it is a valid request
                        requestOk = True
                        errors = []

                        newRequest = json.loads(command.replace('newRequest ', '', 1))
                        
                        if myCustomer.isLoaded():
                            newRequest['Demand'] = int(newRequest['Demand'])
                            newRequest['RevealTime'] = int(newRequest['RevealTime'])
                            newRequest['ServiceDuration'] = int(newRequest['ServiceDuration'])
                            newRequest['TimeWindow']['start'] = int(newRequest['TimeWindow']['start'])
                            newRequest['TimeWindow']['end'] = int(newRequest['TimeWindow']['end'])
                            newRequest['Node'] = int(newRequest['Node'])
                            if int(newRequest['Demand']) < 0:
                                requestOk = False
                                errors += ['Negative Demand']
                            if self.simulationStatus == 'PreSimulation':
                                if int(newRequest['RevealTime']) < -1:
                                    requestOk = False
                                    errors += ['RevealTime < -1']
                                if int(newRequest['RevealTime']) > myCustomer.getHorizonSize():
                                    requestOk = False
                                    errors += ['RevealTime after horizon size']
                            elif self.simulationStatus == 'OfflineEnd':
                                if int(newRequest['RevealTime']) < 0:
                                    requestOk = False
                                    errors += ['RevealTime in offlineTime, but offline simulation is finished']
                                if int(newRequest['RevealTime']) > myCustomer.getHorizonSize():
                                    requestOk = False
                                    errors += ['RevealTime after horizon size']
                            if int(newRequest['ServiceDuration']) < 0:
                                requestOk = False
                                errors += ['NegativeServiceDuration']
                            if int(newRequest['TimeWindow']['start']) > int(newRequest['TimeWindow']['end']):
                                requestOk = False
                                errors += ['start>end']
                            if int(newRequest['TimeWindow']['start']) < 0:
                                requestOk = False
                                errors += ['start<0']
                            elif int(newRequest['TimeWindow']['start']) > myCustomer.getHorizonSize():
                                requestOk = False
                                errors += ['start>horizon']
                            if int(newRequest['TimeWindow']['end']) < 0:
                                requestOk = False
                                errors += ['end<0']
                            elif int(newRequest['TimeWindow']['end']) > myCustomer.getHorizonSize()+1:
                                requestOk = False
                                errors += ['end>horizon']
                        else:
                            requestOk = False
                            errors += ['Customer File Not loaded']
                        if myGraph.isLoaded():
                            if myGraph.containsNode(newRequest['Node']):
                                if 'Customer' not in myGraph.getNodeType(newRequest['Node']):
                                    requestOk = False
                                    errors += ['NotCustomerTypeNode']
                            else:
                                requestOk = False
                                errors += ['NodeNotInGraph']
                        else:
                            requestOk = False
                            errors += ['Graph File Not loaded']

                        if requestOk:
                            # If no error with the new request data, it can be added to the scenario
                            newRequest['TimeSlot'] = myCustomer.getTimeSlotOfTimeUnit(newRequest['RevealTime'])
                            newRequest['Type']     = 'Manual'
                            if self.simulationStatus in ['PreSimulation']:
                                myScenario.addNewRequest(newRequest)
                                self.sendToGUI(('scenarioData', myScenario.data))
                            elif self.simulationStatus == 'OfflineEnd' and newRequest['RevealTime'] >= 0:
                                myScenario.addNewRequest(newRequest)
                                self.sendToGUI(('scenarioData', myScenario.data))
                            elif self.simulationStatus in ['OfflineComputation', 'OfflinePauseAsked', 'OfflinePause']:
                                if newRequest['RevealTime'] >= 0:
                                    myScenario.addNewRequest(newRequest)
                                    self.sendToGUI(('scenarioData', myScenario.data))
                                else:
                                    self.sendToGUI(('error', 'Impossible to add offline request after start of Offline Computation'))
                            elif self.simulationStatus in ['OnlineComputation', 'OnlinePauseAsked', 'OnlinePause']:
                                # if a simulation is running, the simulation thread must verify the current TU and decide to add or not the new request
                                # the validity of the new request was verified in this thread
                                self.downQueue.put(command)
                            
                        else:
                            errorMsg = 'Impossible to add the request due to the following error(s) :'
                            for error in errors:
                                errorMsg += '\n'+error
                            self.sendToGUI(('error', errorMsg))
                            print('   ERROR: the new request could not be added because of the following error(s):\n'+errorMsg[61:])

                            
                        self.printLog('User command : newRequest')
                    else:
                        print('   ERROR: new requests can not be added after the simulation')

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()

                elif commandSplit == ['offlineTime']:
                    if 'OfflineTime' not in myFiles or myFiles['OfflineTime'] == None:
                        print('The offline time is not defined\nUse command "setOfflineTime" to set the offlineTime time')
                    else:
                        print('OfflineTime set to {} seconds'.format(myFiles['OfflineTime']))
                    self.eventCommand.set()

                elif commandSplit == ['pause']:
                    if self.simulationStatus in ['OfflineComputation']:
                        self.downQueue.put('pause')
                        self.changeStatusTo('OfflinePauseAsked')
                        self.printLog('User command : pause')

                    elif self.simulationStatus in ['OnlineComputation']:
                        self.downQueue.put('pause')
                        self.changeStatusTo('OnlinePauseAsked')
                        self.printLog('User command : pause')

                    elif self.simulationStatus in ['OfflinePauseAsked', 'OnlinePauseAsked']:
                        print('   ERROR: a pause was already asked, but did not start yet')

                    elif self.simulationStatus in ['OfflinePause', 'OnlinePause']:
                        print('   ERROR: the simulation is already in pause')

                    else:
                        print('   ERROR: there is currently no simulation running')

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()

                elif commandSplit == ['printCarrier']:
                    myCarrier.display()
                    self.printLog('User Command : printCarrier')
                    self.eventCommand.set()
                    
                elif commandSplit == ['printCustomers']:
                    myCustomer.display()
                    self.printLog('User command : printCustomers')
                    self.eventCommand.set()
                    
                elif commandSplit == ['printGraph']:
                    myGraph.display()
                    self.printLog('User command : printGraph')
                    self.eventCommand.set()
                    
                elif commandSplit == ['printScenario']:
                    myScenario.display()
                    self.printLog('User command : printScenario')
                    self.eventCommand.set()

                elif commandSplit[0] == 'printSolverSolution':
                    shortFlag = len(commandSplit) == 2 and commandSplit[1] == 'short'
                    self.mySolutions.printLastSolution(short = shortFlag)
                    self.printLog('User command : printSolverSolution')
                    self.eventCommand.set()

                elif commandSplit[0] == 'printUserSolution':
                    shortFlag = len(commandSplit) == 2 and commandSplit[1] == 'short'
                    self.mySolutions.printUserSolution(short = shortFlag)
                    self.printLog('User command : printSolution')
                    self.eventCommand.set()

                elif commandSplit[0] == 'saveUserSolution':
                    command = command.replace('saveUserSolution ', '', 1)
                    with open(command, 'w') as outfile:
                        json.dump(self.mySolutions.data['UserSolution'], outfile, sort_keys=True, indent = 4)
                        self.printLog('User command saveUserSolution')

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()

                elif commandSplit[0] == 'saveScenario':
                    if not myScenario.data:
                        print('   Error: no scenario in memory')
                    else:
                        filename = command.replace('saveScenario ', '', 1)

                        if os.path.exists(filename): # modify the output file name if already exists
                            (fileroot, fileext) = os.path.splitext(filename)
                            extNum = 1
                            while os.path.exists(fileroot+'('+str(extNum)+')'+fileext):
                                extNum += 1
                            filename = fileroot+'('+str(extNum)+')'+fileext.rstrip('\n')
                        
                        with open(filename, 'w') as outfile:
                            json.dump(myScenario.data, outfile, sort_keys=True, indent = 4)
                            self.printLog('User command : saveScenario')

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()
                        
                elif command.startswith('saveSolutions '):
                    filename = command.replace('saveSolutions ', '', 1)

                    if os.path.exists(filename): # modify the output file name if already exists
                        (fileroot, fileext) = os.path.splitext(filename)
                        extNum = 1
                        while os.path.exists(fileroot+'('+str(extNum)+')'+fileext):
                            extNum += 1
                        filename = fileroot+'('+str(extNum)+')'+fileext.rstrip('\n')


                    with open(filename, 'w') as outfile:
                        json.dump(self.mySolutions.data, outfile, sort_keys=True, indent = 4)
                        self.printLog('User command saveSolutions')

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()

                elif commandSplit[0] == 'saveLastSolution':
                    if len(commandSplit) > 1:
                        filename = commandSplit[1]
                        if os.path.exists(filename): # modify the output file name if already exists
                            (fileroot, fileext) = os.path.splitext(filename)
                            extNum = 1
                            while os.path.exists(fileroot+'('+str(extNum)+')'+fileext):
                                extNum += 1
                            filename = fileroot+'('+str(extNum)+')'+fileext.rstrip('\n')
                        if len(self.mySolutions.data['Solutions']) > 0:
                            try:
                                outfile = open(filename, 'w')
                                json.dump(self.mySolutions.data['Solutions'][-1], outfile, sort_keys=True, indent = 4)
                                outfile.close()
                            except (OSError, IOError, TypeError, OverflowError, ValueError) as e:
                                print("Error while trying to save the last solution: {}".format(e))
                            except:
                                print("Unidentified Error while trying to save the last solution :", sys.exc_info()[0])
                    else:
                        print("No file provided")



                elif commandSplit == ['sendAll']:
                    if self.simulationStatus not in ['PostSimulation']:
                        if not self.simuAPI.testConnection():
                            self.sendToGUI(('error','solver not connected'))
                            print('   ERROR: No solver connected')
                        else:
                            self.printLog('User command : sendEverything')
                            if not not myCarrier.data:
                                self.simuAPI.sendCarrierJsonToSolver(json.dumps(myCarrier.data))
                                self.removeFromDataNotSent('Carrier')
                                self.addToDataSent('Carrier')
                                print('  Carrier sent')
                                self.printLog('sendCarrierToSolver')
                            if not not myCustomer.data:
                                self.simuAPI.sendCustomersJsonToSolver(json.dumps(myCustomer.data))
                                self.removeFromDataNotSent('Customer')
                                self.addToDataSent('Customer')
                                print('  Customer sent')
                                self.printLog('sendCustomersToSolver')
                            if not not myGraph.data:
                                self.simuAPI.sendGraphJsonToSolver(json.dumps(myGraph.data))
                                self.removeFromDataNotSent('Graph')
                                self.addToDataSent('Graph')
                                print('  Graph sent')
                                self.printLog('sendGraphToSolver')
                            for key in myFiles:
                                jsonMsg = '{ "' + key + '" :' + str(json.dumps(myFiles[key])) + '}'
                                self.simuAPI.sendFile(jsonMsg)
                                self.removeFromDataNotSent(key)
                                self.addToDataSent(key)
                                print('  '+str(key)+' sent')
                                self.printLog('User command : send file loaded as %s' % ( str(key)))
                    else:
                        print('   ERROR: data can not be sent after the end of the simulation')

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()

                elif commandSplit == ['sendCarrierToGUI']:
                    self.guiQueue.put(('carrierData', myCarrier.data))

                elif commandSplit == ['sendCustomersToGUI']:
                    self.sendToGUI(('customerData', myCustomer.data))

                elif commandSplit == ['sendGraphToGUI']:
                    self.sendToGUI(('graphData', myGraph.data))

                elif commandSplit == ['sendScenarioToGUI']:
                    self.sendToGUI(('scenarioData', myScenario.data))

                elif commandSplit == ['sendCarrierToSolver']:
                    if self.simulationStatus not in ['PostSimulation']:
                        if not self.simuAPI.testConnection():
                            print('   ERROR: No solver connected')
                        else:
                            if not not myCarrier.data:
                                self.simuAPI.sendCarrierJsonToSolver(json.dumps(myCarrier.data))
                                self.removeFromDataNotSent('Carrier')
                                self.addToDataSent('Carrier')
                                print('  Carrier sent')
                                self.printLog('User command : sendCarrierToSolver')
                            else : 
                                print('   Carrier is empty. Did you use loadCarrier ? ')
                                self.printLog('User command : sendCarrierToSolver \n Error: Carrier is empty')
                    else:
                        print('   ERROR: data can not be sent after the end of the simulation')

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()
                    
                elif commandSplit == ['sendCustomersToSolver']:
                    if self.simulationStatus not in ['PostSimulation']:
                        if not self.simuAPI.testConnection():
                            print('   ERROR: No solver connected')
                        else:
                            if not not myCustomer.data:
                                self.simuAPI.sendCustomersJsonToSolver(json.dumps(myCustomer.data))
                                self.removeFromDataNotSent('Customer')
                                self.addToDataSent('Customer')
                                print('  Customer sent')
                                self.printLog('User command : sendCustomersToSolver')
                            else : 
                                print('   Customer is empty. Did you use loadCustomer ? ')
                                self.printLog('User command : sendCustomersToSolver \n Error: Customer is empty')
                    else:
                        print('   ERROR: data can not be sent after the end of the simulation')

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()

                elif command.startswith('sendFile '):
                    if self.simulationStatus not in ['PostSimulation']:
                        if not self.simuAPI.testConnection():
                            print('   ERROR: No solver connected')
                        else:
                            command = command.replace('sendFile', '', 1).split()
                            key = command[-1]
                            fileName = ' '.join(command[:len(command)-1])
                            try:
                                myFiles[key] = json.load(open(fileName))
                                jsonMsg = '{ "' + key + '" :' + str(json.dumps(myFiles[key])) + '}'
                                self.simuAPI.sendFile(jsonMsg)
                                self.removeFromDataNotSent(key)
                                self.addToDataSent(key)
                                print('  '+str(key)+' sent')
                                self.printLog('User command : sendFile %s %s' % (str(fileName), str(key)))
                            except IOError:
                                print('   Error: cannot send the file', fileName) 
                                self.printLog('User command : sendFile %s %s \n Error: cannot send the file %s' % (str(fileName), str(key), str(fileName)))
                    else:
                        print('   ERROR: data can not be sent after the end of the simulation')

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()
                    
                elif commandSplit == ['sendGraphToSolver']:
                    if self.simulationStatus not in ['PostSimulation']:
                        if not self.simuAPI.testConnection():
                            print('   ERROR: No solver connected')
                        else:
                            if not not myGraph.data:
                                self.simuAPI.sendGraphJsonToSolver(json.dumps(myGraph.data))
                                self.removeFromDataNotSent('Graph')
                                self.addToDataSent('Graph')
                                print('  Graph sent')
                                self.printLog('User command : sendGraphToSolver')
                            else : 
                                print('   Graph is empty. Did you use loadGraph ? ')
                                self.printLog('User command : sendGraphToSolver \n Error: Graph is empty')
                    else:
                        print('   ERROR: data can not be sent after the end of the simulation')

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()

                elif command.startswith('setComputationTime '):
                    if self.simulationStatus in ['PreSimulation', 'OfflineComputation', 'OfflinePauseAsked', 'OfflinePause', 'OfflineEnd']:
                        if simulationStarted:
                            print('   It is not allowed to change the computation time during the simulation')
                        else:
                            command = commandSplit
                            if len(command) is 1:
                                print('   Error: missing computation time in argument')
                                self.printLog('User command : setComputationTime : Error: missing computation time in argument')
                            if len(command) > 2:
                                print('   Error: to many argument')
                                self.printLog('User command : setComputationTime : Error: to many argument')

                            if len(command) is 2:
                                myFiles["ComputationTime"] = float(command[1])
                                myScenario.data["ComputationTime"] = float(command[1])
                                self.addToDataNotSent('ComputationTime')
                                self.removeFromDataSent('ComputationTime')
                                self.printLog('User command : setComputationTime ' + command[1])
                    elif self.simulationStatus in ['PostSimulation']:
                        print('   ERROR: the computation time can not be changed after the simulation')
                    elif self.simulationStatus in ['OnlineComputation', 'OnlinePause', 'OnlinePauseAsked']:
                        print('   ERROR: the computation time can not be changed during the simulation')

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()

                elif command.startswith('setLogFile '):
                    command = command.replace('setLogFile ', '', 1)
                    try:
                        self.logFile = command
                        lf = open(self.logFile, 'w')
                        lf.write(str(time.asctime( time.localtime(time.time()) )) + ' : User Command  : setLogFile ' + ' \n\n')
                        lf.close()
                        if simulationStarted:
                            self.downQueue.put('logFile %s ' % command)
                    except IOError:
                        print('   cannot open file', command)

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()

                elif command.startswith('setOfflineTime '):
                    if self.simulationStatus in ['PreSimulation']:
                        if simulationStarted:
                            print('   It is not allowed to change the OfflineTime time during the simulation')
                        else:
                            command = commandSplit
                            if len(command) is 1:
                                print('   Error: missing offline time in argument')
                                self.printLog('User command : setOfflineTime : Error: missing offline time in argument')

                            if len(command) > 2:
                                print('   Error: to many argument')
                                self.printLog('User command : setOfflineTime : Error: to many argument')

                            if len(command) is 2:
                                myFiles["OfflineTime"] = float(command[1])
                                myScenario.data["OfflineTime"] = float(command[1])
                                self.addToDataNotSent('OfflineTime')
                                self.removeFromDataSent('OfflineTime')
                                self.printLog('User command : setOfflineTime ' + command[1])
                    else:
                        print('   ERROR: the offline time can only be changed before starting the simulation')

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()

                elif commandSplit[0] == 'setVehicleCapacity':
                    if self.simulationStatus != 'PreSimulation':
                        print('   Error: The fleet of vehicles can be modified only before the simulation')
                    else:
                        if not myCarrier.data:
                            print('   Error: No Carrier file is loaded')
                        else:
                            validArgs = True
                            if len(commandSplit) is 1:
                                validArgs = False
                                print('   Error: missing capacities and types of vehicles to be modified')
                                self.printLog('User command: ' + command + ' : Error:  missing capacities and types of vehicles to be modified')
                            
                            elif len(commandSplit)%2 is 0:
                                validArgs = False
                                print('   Error: the number of argument is not correct')
                                self.printLog('User command: ' + command + ' Error: the number of argument is not correct')
                            
                            elif len(commandSplit)%2 is 1:
                                expect = 'VehicleType'
                                for arg in commandSplit[1:]:
                                    # loop that should altern number and vehicleType
                                    if expect == 'Number':
                                        if not arg.isdigit():
                                            validArgs = False
                                            print('   Error: '+arg+' is not a number')
                                        expect = 'VehicleType'
                                    elif expect == 'VehicleType':
                                        if not myCarrier.containVehicleType(arg):
                                            validArgs = False
                                            print('   Error: '+arg+' is not a vehicle type in the carrier file')
                                        expect = 'Number'
                        
                            if validArgs:
                                # iterate on the number on the command
                                cs = commandSplit
                                noError = True
                                for num in range(1, len(cs), 2):
                                    if not str.isdigit(cs[num+1]):
                                        noError = False
                                        print('   Error: invalid argument : '+cs[num+1]+' should be a number')
                                        self.printLog('User command :'+command+' : Error: invalid argument : '+cs[num+1]+' should be a number')
                                    
                                    # check if vehicle type is in the available vehicle types
                                    if cs[num] not in [k['VehicleType'] for k in myCarrier.data['VehicleTypes']]:
                                        noError = False
                                        print('   Error: invalid argument : "'+cs[num]+'" is not an available type of vehicle')
                                        self.printLog('User command : '+command+' : Error: invalid argument : "'+cs[num]+'" is not an available type of vehicle')

                                if noError:
                                    # modify the capacity
                                    for num in range(1, len(cs), 2):
                                        for vehicleType in myCarrier.data['VehicleTypes']:
                                            if vehicleType['VehicleType'] == cs[num]:
                                                vehicleType['Capacity'] = int(cs[num+1])

                                    
                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()

                elif commandSplit[0] == 'showVehicles':
                    if not myCarrier.data:
                        print('   Error: no carrier file loaded')
                        self.printLog('User command : showVehicles : Error : no carrier file loaded')
                    elif 'Vehicles' not in myCarrier.data.keys() or not myCarrier.data['Vehicles']:
                        print('   There is no vehicles available for the solver')
                        self.printLog('User command : showVehicles')
                    else:
                        vCount = {}
                        vOrdered = {}
                        for key, value in myCarrier.data['Vehicles'].items():
                            if value['VehicleType'] not in vCount.keys():
                                vCount[value['VehicleType']] = 1
                            else:
                                vCount[value['VehicleType']] += 1
                            vOrdered[int(key)] = value
                        vOrdered = [{str(k): vOrdered[k]} for k in sorted(vOrdered)]
                        for el in vOrdered:
                            pprint(el)

                        for vt in vCount.keys():
                            print('   Number of "'+vt+'": ' + str(vCount[vt]))

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()


                elif commandSplit[0] == 'showVehicleType':
                    if 'VehicleTypes' in myCarrier.data.keys():
                        for vt in myCarrier.data['VehicleTypes']:
                            pprint(vt)  
                    elif not myCarrier.data:
                        print('   Error: please load a carrier file')
                    else:
                        print('   Error: it seems no VehiclesTypes where given in the loaded file')

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()

                elif commandSplit[0] == 'setVehicleColor':
                    if len(commandSplit) == 3:
                        myCarrier.setVehicleColor(commandSplit[1], commandSplit[2])
                    else:
                        print('    Error: {} : invalid number of argument : {} instead of 3'.format(command, len(commandSplit)))

                elif commandSplit == ['startOfflineSimulation']:
                    simulationThreadLaunched = False
                    if self.simulationStatus in ['PreSimulation']:
                        if simulationStarted:
                            print('   A simulation is already running')
                        else:
                            connectionOK = dataAvailable = True
                            

                            # check solver connected
                            if not self.simuAPI.testConnection():
                                connectionOK = False
                                self.sendToGUI(('error', 'solver not connected, impossible to start the offline simulation'))
                                print('      solver not connected')

                            # check all necessary data is here
                            elif not myCustomer.data or not myGraph.data or not myScenario.data or not myCarrier.data or 'OfflineTime' not in myFiles: 
                                print('    cannot launch simulation due to the following problems:')
                                dataAvailable = False
                                if not myCustomer.data:
                                    print('      Customer file missing')
                                    self.sendToGUI(('error', 'the customer file is missing, impossible to start the offline simulation'))
                                if not myCarrier.data:
                                    print('      Carrier file missing')
                                    self.sendToGUI(('error', 'the carrier file is missing, impossible to start the offline simulation'))
                                if not myGraph.data:
                                    print('      Graph file missing')
                                    self.sendToGUI(('error', 'the graph file is missing, impossible to start the offline simulation'))
                                if not myScenario.data:
                                    print('      Scenario file missing')
                                    self.sendToGUI(('error', 'the scenario file is missing, impossible to start the offline simulation'))
                                if 'OfflineTime' not in myFiles:
                                    print('      OfflineTime missing')
                                    self.sendToGUI(('error', 'the OfflineTime is missing, impossible to start the offline simulation'))


                            if connectionOK and dataAvailable:
                                allDataWasSent = True
                                # send computation and offline time if only these have not been sent
                                if all([i == 'OfflineTime' for i in self.dataNotSent ]):
                                    for data in self.dataNotSent:
                                        jsonMsg = '{ "' + data + '" :' + str(json.dumps(myFiles[data])) + '}'
                                        self.simuAPI.sendFile(jsonMsg)
                                        self.addToDataSent(data)
                                    # do not modify what we iterate on while we iterate on it
                                    self.dataNotSent = []

                                # inform user if some data need to be sent before starting simulation
                                elif len(self.dataNotSent) > 0:
                                    errorMsg = 'The file(s) '
                                    allDataWasSent = False
                                    for data in self.dataNotSent:
                                        if data != 'OfflineTime':
                                            errorMsg += '"'+data+'"'
                                            print('   Error: '+data+' was not sent to the solver')
                                            print('       please send '+data+' before starting the simulation')
                                    self.sendToGUI(('error', errorMsg + ' were not sent to the solver. Impossible to start the offline Simulation'))

                                if allDataWasSent:
                                    myScenario.markInitialRequest(myCustomer.data)
                                    self.mySolutions.realDurationPerTimeUnit = myCustomer.data['RealDurationPerTimeUnit']
                                    self.mySolutions.realTimeUnit = myCustomer.data['RealTimeUnit']
                                    self.mySolutions.carrierUnit = myCarrier.data['Unit']
                                    mySimulation = Simulation.simulationOfflineThread(myScenario, self.downQueue, self.upQueue, self.logFileLock, self.simuAPI, self.simulationQueue, self.eventSMQueue, self.eventLock, self.logFile)                        
                                    mySimulation.start()
                                    simulationThreadLaunched = True
                                    self.changeStatusTo('OfflineComputation')
                                    self.solverStatus = 'OfflineComputation'
                                    self.printLog('User command : startOfflineSimulation')
                                    

                    elif self.simulationStatus in ['OfflineComputation', 'OfflinePauseAsked', 'OfflinePause']:
                        print('   ERROR: the offline simulation has already begun')
                    elif self.simulationStatus in ['OfflineEnd']:
                        print('   ERROR: the offline simulation has already happend')
                    elif self.simulationStatus in ['OnlineComputation', 'OnlinePauseAsked', 'OnlinePause']:
                        print('   ERROR: the simulation is currently in the online phase')
                    elif self.simulationStatus in ['PostSimulation']:
                        print('   ERROR: the simulator is in post simulation status. Use the command "stopSimulation" to go back to the pre simulation status')
                        
                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    if not self.scriptMode or not simulationThreadLaunched:
                        self.eventCommand.set()

                elif commandSplit == ['startOnlineSimulation']:
                    simulationThreadLaunched = False
                    if self.simulationStatus in ['PreSimulation']:
                        print('   The offline simulation was not executed. Please start the offline simulation before the online simulation')
                    if self.simulationStatus in ['OfflineEnd']:
                        if simulationStarted:
                            print('   A simulation is already running')
                        else:
                            connectionOK = dataAvailable = True
                            initialSolution = self.mySolutions.containsValidInitialOfflineSolution(myScenario)
                            # check all necessary data is here
                            if not myCustomer.data or not myGraph.data or not myScenario.data or not myCarrier.data or'ComputationTime' not in myFiles or initialSolution == False :
                                print('    cannot launch simulation due to the following problems:')
                                dataAvailable = False
                                if not myCustomer.data:
                                    print('      Customer file missing')
                                if not myCarrier.data:
                                    print('      Carrier file missing')
                                if not myGraph.data:
                                    print('      Graph file missing')
                                if not myScenario.data:
                                    print('      Scenario file missing')
                                if 'ComputationTime' not in myFiles:
                                    print('      ComputationTime missing')
                                if initialSolution == False:
                                    print('      Initial offline solution missing')

                            # check solver connected
                            if not self.simuAPI.testConnection():
                                connectionOK = False
                                print('      solver not connected')

                            if connectionOK and dataAvailable:
                                allDataWasSent = True

                                # send computation time if not sent, but ignore offline time
                                if all([i == 'ComputationTime' or i == 'OfflineTime' for i in self.dataNotSent ]):
                                    # send an initial solution
                                    self.simuAPI.setCurrentSolution(json.dumps(initialSolution))
                                    for data in self.dataNotSent:
                                        if data == 'ComputationTime':
                                            jsonMsg = '{ "' + data + '" :' + str(json.dumps(myFiles[data])) + '}'
                                            self.simuAPI.sendFile(jsonMsg)
                                            self.addToDataSent(data)
                                    self.dataNotSent = []

                                # inform user if some data need to be sent before starting simulation
                                elif len(self.dataNotSent) > 0:
                                    allDataWasSent = False
                                    for data in self.dataNotSent:
                                        if data != 'ComputationTime':
                                            print('   Error: '+data+' was not sent to the solver')
                                            print('       please send '+data+' before starting the simulation')

                                if allDataWasSent:
                                    self.mySolutions.realDurationPerTimeUnit = myCustomer.data['RealDurationPerTimeUnit']
                                    self.mySolutions.realTimeUnit = myCustomer.data['RealTimeUnit']
                                    self.mySolutions.carrierUnit = myCarrier.data['Unit']

                                    mySimulation = Simulation.simulationOnlineThread(myScenario, self.downQueue, self.upQueue, myCustomer.data["HorizonSize"], self.logFileLock, self.simuAPI, self.simulationQueue, self.eventSMQueue, self.eventLock, self.logFile)                        
                                    mySimulation.start()
                                    simulationThreadLaunched = True
                                    self.changeStatusTo('OnlineComputation')
                                    self.solverStatus = 'OnlineComputation'
                                    self.printLog('User command : startSimulation')

                    elif self.simulationStatus in ['OfflineComputation', 'OfflinePauseAsked', 'OfflinePause']:
                        print('   ERROR: the offline simulation is already running')
                    elif self.simulationStatus in ['OnlineComputation', 'OnlinePauseAsked', 'OnlinePause']:
                        print('   ERROR: the online simulation is already running')
                    elif self.simulationStatus in ['PostSimulation']:
                        print('   ERROR: the simulator is in post simulation mode. Use the command "stopSimulation" to go back to the pre simulation mode')
                               
                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    if not self.scriptMode or not simulationThreadLaunched:
                        self.eventCommand.set()

                elif commandSplit == ['stopSimulation']:

                    self.stopSimulation(self.mySolutions, mySimulation)
                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()

                        
                elif command.startswith('test ') or commandSplit == ['test']:
                    print('\n     You make the command "test"')
                    command = command.replace('test', '', 1)
                    try:
                        args = vars(testParser.parse_args(commandSplit))
                        print(args)
                        for key in args:
                            if args[key] is not None:
                                print(key)
                                if key == 'path':
                                    print(' '.join(args[key]))
                                else:
                                    print(args[key])
                        self.printLog('User command : test')
                    except SystemExit:
                        pass

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()

                elif commandSplit == ['testConnection']:
                    if self.simuAPI.testConnection():
                        print('   solver connected')
                        self.printLog('User command : testConnection : solver connected')
                    else:
                        print('   solver not connected')
                        self.printLog('User command : testConnection : solver not connected')

                    if verbose:
                        print('   SimulationManager :: serve command :: ', command)
                    self.eventCommand.set()
  
                else:
                    print('   command incorrect')
                    self.printLog('User command : incorrect command : %s ' % command)
                    self.eventCommand.set()

                # notify the userinput manager that command was handled
                if not self.scriptMode:
                    self.eventCommand.set()
            
            #manage the message from the simulation thread 
            while not self.upQueue.empty():
                message = self.upQueue.get()
                if message[0].startswith('newRequest '):
                    newRequest = json.loads(command.replace('newRequest ', '', 1))
                    myScenario.addNewRequest(newRequest)
                    self.sendToGUI(('scenarioData', myScenario.data))

                elif message[0] == 'newTimeUnit':
                    self.mySolutions.newSolutionForDisplay(myGraph.data, myCarrier.data, message[1])


                elif message[0] == 'endOfSimulation':
                    if self.simulationStatus in ['OnlineComputation', 'OnlinePauseAsked']:
                        self.simuAPI.sendCloseMessage()
                        self.printLog('End of Simulation')
                        self.changeStatusTo('PostSimulation')
                        print('   End of the simulation')
                    else:
                        print('   ERROR: SimulationManager thread receive a "endOfSimulation" message from the simulation thread')
                        print('          but the current status of the simulation is: ', self.simulationStatus)
                        self.simuAPI.sendCloseMessage()
                        self.printLog('End of Simulation')
                        self.changeStatusTo('PostSimulation')
                        print('   End of the simulation')

                elif message[0] == 'startOfflinePause':
                    if self.simulationStatus in ['OfflinePauseAsked']:
                        self.sendToGUI(message)
                        self.changeStatusTo('OfflinePause')
                    else:
                        print('   ERROR: SimulationManager thread receive "startOfflinePause" message from simulation thread')
                        print('          but the current simulationStatus is : ', self.simulationStatus)
                        print('          The simulationStatus will now be set to "PreSimulation"')
                        self.changeStatusTo('PreSimulation')

                elif message[0] == 'endOfflinePause':
                    if self.simulationStatus in ['OfflinePause']:
                        self.sendToGUI(message)
                        self.changeStatusTo('OfflineComputation')
                        self.solverStatus = 'OfflineComputation'
                    else:
                        print('   ERROR: SimulationManager thread receive "endOfflinePause" message from simulation thread')
                        print('          but the current simulationStatus is : ', self.simulationStatus)
                        print('          The simulationStatus will now be set to "PreSimulation"')
                        self.changeStatusTo('PreSimulation')

                elif message[0] == 'endOfOfflineSimulation':
                    self.downQueue.put('closeThread')
                    mySimulation.join()
                    if self.simulationStatus in ['OfflineComputation', 'OfflinePauseAsked']:
                        self.changeStatusTo('OfflineEnd')

                    else:
                        print('   ERROR: SimulationManager thread receive "endOfOfflineSimulation" message from simulation thread')
                        print('          but the current simulationStatus is : ', self.simulationStatus)
                        print('          The simulationStatus will now be set to "OfflineEnd"')
                        self.changeStatusTo('OfflineEnd')

                    # if script mode, solver finish offline and simu finish offline, we can take next script command
                    if self.solverStatus == 'OfflineEnd':
                        if self.scriptMode:
                            self.eventCommand.set()
                        print('   END OF THE OFFLINE SIMULATION')


                elif message[0] == 'startOnlinePause':
                    if self.simulationStatus in ['OnlinePauseAsked']:
                        self.sendToGUI(message)
                        self.changeStatusTo('OnlinePause')
                    else:
                        print('   ERROR: SimulationManager thread receive "startOnlinePause" message from simulation thread')
                        print('          but the current simulationStatus is : ', self.simulationStatus)
                        print('          The simulationStatus will now be set to "PreSimulation"')
                        self.changeStatusTo('PreSimulation')

                elif message[0] == 'endOnlinePause':
                    if self.simulationStatus in ['OnlinePause']:
                        self.sendToGUI(message)
                        self.changeStatusTo('OnlineComputation')
                    else:
                        print('   ERROR: SimulationManager thread receive "endOfflinePause" message from simulation thread')
                        print('          but the current simulationStatus is : ', self.simulationStatus)
                        print('          The simulationStatus will now be set to "PreSimulation"')
                        self.changeStatusTo('PreSimulation')

                elif message[0] == 'endOfOnlineSimulation':
                    self.downQueue.put('closeThread')
                    mySimulation.join()
                    if self.simulationStatus in ['OnlineComputation', 'OnlinePauseAsked']:
                        self.changeStatusTo('PostSimulation')

                    else:
                        print('   ERROR: SimulationManager thread receive "endOfOfflineSimulation" message from simulation thread')
                        print('          but the current simulationStatus is : ', self.simulationStatus)
                        print('          The simulationStatus will now be set to "PostSimulation"')
                        self.changeStatusTo('PostSimulation')

                elif message[0] == 'startTimeOffline':
                    # transmit the startTime decided by simulation thread to the GUI
                    self.sendToGUI(message)

                elif message[0] == 'startTimeOnline':
                    # transmit the startTime decided by simulation thread to the GUI
                    self.sendToGUI(message)


                #error message from the api
                elif message == 'RpcError : Connect Failed':
                    self.simuAPI = simulatorAPI(self.pauseMessageQueue, self.upQueue, self.eventSMQueue, self.eventLock)

                    if self.simulationStatus in ['OfflineComputation', 'OfflinePauseAsked', 'OfflinePauseAsked', 'OfflineEnd', 'OnlineComputation', 'OnlinePauseAsked', 'OnlinePause']:
                        self.downQueue.put('RpcError : close')
                        self.changeStatusTo('PreSimulation')
                        self.solverStatus = 'PreSimulation'
                        for data in self.dataSent:
                            self.addToDataNotSent(data)
                        self.dataSent = []
                        self.mySolutions = Solution()

                    elif self.simulationStatus in ['PreSimulation', 'PostSimulation']:
                        pass
                else:
                    print('ERROR: message in the upQueue not understood "{}"'.format(message))



            # add all the new solutions send by the solver
            while not self.solutionsQueue.empty():
                queueElement = self.solutionsQueue.get()
                if queueElement[0] == 'updateBestSolution':
                    # new best solution from the solver via the simulator listener thread
                    newSolution = json.loads(queueElement[1])
                    if self.mySolutions.isSolutionValid(newSolution, myGraph.data, myCarrier, myScenario, myCustomer.data["TimeSlots"]):
                        if self.scriptMode:
                            # print('   New VALID solution, total of  : ' + str(len(self.mySolutions.data['Solutions'])), end = '\r' )
                            numberValid   = len(self.mySolutions.data['Solutions'])
                            numberInvalid = len(self.mySolutions.data['SolutionsNotValid'])
                            print('   # valid solution     {}  #invalid solution {}   total number of solution {}'
                                .format(numberValid, numberInvalid, numberValid + numberInvalid), end = '\r')
                        elif verbose:
                            print('   New VALID solution, total of  : ' + str(len(self.mySolutions.data['Solutions'])))
                        self.mySolutions.updateBestSolution(newSolution)
                        
                        self.mySolutions.newSolutionForDisplay(myGraph.data, myCarrier.data)

                        self.sendToGUI(('updateBestSolution', newSolution))
                    else:
                        if self.scriptMode:
                            numberValid   = len(self.mySolutions.data['Solutions'])
                            numberInvalid = len(self.mySolutions.data['SolutionsNotValid'])
                            print('   number of valid solution     {}  total number of invalid solution {}   total number of solution {}'
                                .format(numberValid, numberInvalid, numberValid + numberInvalid), end = '\r')
                        elif verbose:
                            print('   New NONVALID Solution, total of : ' + str(len(self.mySolutions.data['Solutions'])))
                        if self.mySolutions.data['NumberOfSolutions'] > 0 :
                            # Send the last valid solution to the solver
                            self.simuAPI.setCurrentSolution(json.dumps(self.mySolutions.data['Solutions'][-1]))
                        else:
                            # send an empty solution with the time of submission
                            self.downQueue.put('sendEmptySolutionWithTOS')
                        self.mySolutions.data["SolutionsNotValid"] += [newSolution]
                    self.printLog('newSolution')

                elif queueElement[0] == 'acceptedRequest':
                    #confirm that a request is accepted, should only occurs during computation
                    if self.solverStatus in ['OfflineComputation', 'OfflinePauseAsked', 'OnlineComputation', 'OnlinePauseAsked']:
                        request = json.loads(queueElement[1])
                        requestAccepted = self.mySolutions.acceptRequest(request, myScenario)
                        if requestAccepted != True:
                            # if an error occurs, print the message returned by the function
                            # and stop the simulation
                            print(requestAccepted)
                            self.stopSimulation(self.mySolutions, mySimulation)
                        else:
                            # if request is accepted, notify the GUI
                            self.sendToGUI(('acceptedRequest', request))

                    else:
                        print('   ERROR: receive accept request message from solver')
                        print('          but the solver status should be ', self.solverStatus)


                elif queueElement[0] == 'SolverEndOffline':
                    # Solver confirm end of offline, no more offline solution will arrive
                    if self.solverStatus == 'OfflineComputation':
                        self.solverStatus = 'OfflineEnd'
                        # if script mode, solver finish offline and simu finish offline, we can take next script command
                        if self.simulationStatus == 'OfflineEnd':
                            numberValid   = len(self.mySolutions.data['Solutions'])
                            numberInvalid = len(self.mySolutions.data['SolutionsNotValid'])
                            print('   END OF THE OFFLINE SIMULATION')
                            print('   # valid solution     {}  #invalid solution {}   total number of solution {}'
                                .format(numberValid, numberInvalid, numberValid + numberInvalid))
                            if self.scriptMode:
                                self.eventCommand.set()
                    else:
                        print('ERROR : ReceiveEndOffline but solver not in offline computation')


                elif queueElement[0] == "SolverEndOnline":
                    # confirmation that the last online sol has been received
                    # self.solverStatus = 'PostSimulation'
                    
                    if self.solverStatus == 'OnlineComputation':
                        self.solverStatus = 'PostSimulation'                        
                        # if script mode, solver finish offline and simu finish offline, we can take next script command
                        if self.simulationStatus == 'PostSimulation':
                            numberValid   = len(self.mySolutions.data['Solutions'])
                            numberInvalid = len(self.mySolutions.data['SolutionsNotValid'])
                            print('   END OF THE ONLINE SIMULATION')
                            print('   SolverEndOnline # valid solution     {}  #invalid solution {}   total number of solution {}'
                                .format(numberValid, numberInvalid, numberValid + numberInvalid))
                            if self.scriptMode:
                                self.eventCommand.set()
                    else:
                        print('--------------------------------------------------ReceiveEndOnline but solver not in online computation')


