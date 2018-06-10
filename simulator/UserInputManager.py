#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 12:49:36 2017

@author: simon
"""

import queue
import threading
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.contrib.completers import WordCompleter




class UIMthread(threading.Thread):

    def __init__(self, commandQueue, eventCommand, eventSMQueue, eventLock):
        threading.Thread.__init__(self)
        self.commandQueue = commandQueue
        self.eventCommand = eventCommand
        self.eventSMQueue = eventSMQueue
        self.eventLock = eventLock
        self.commandCompleter = WordCompleter(['addVehicles',
        'close',
        'continue',
        'createNewSolution',
        'currentStatus',
        'deleteRequest',
        'deleteVehicles',
        'generateScenario',
        'insertRequest',
        'loadCarrier',
        'loadCustomer',
        'loadFile',
        'loadGraph',
        'loadNewSolution',
        'loadScenario',
        'loadUserSolutions',
        'newRequest',
        'pause',
        'printCarrier',
        'printCustomers',
        'printGraph',
        'printScenario',
        'printSolverSolution',
        'printUserSolution',
        'saveUserSolution',
        'saveScenario',
        'saveSolutions',
        'sendCarrierToSolver',
        'sendCustomersToSolver',
        'sendAll',
        'sendFile',
        'sendGraphToSolver',
        'setComputationTime',
        'setVehicleCapacity',
        'setLogFile',
        'setOfflineTime ',
        'showVehicles',
        'showVehicleType',
        'startOfflineSimulation',
        'startOnlineSimulation',
        'stopSimulation',
        'test',
        'testConnection' ], ignore_case = True)
        
    def run(self):
        exitFlag = False
        while not exitFlag:
            
            #TODO: rajouter un lock sur la fonction input pour pas faire buger un éventuel print dans la commande précédente
            command = prompt('--:', history = FileHistory('history.txt'),
                auto_suggest = AutoSuggestFromHistory(),
                completer = self.commandCompleter,
                patch_stdout = True)
            
            if command.split() == ['close']:
                exitFlag = True
            
            if command != '':
                self.eventLock.acquire()
                self.eventCommand.clear()
                self.commandQueue.put(command)
                self.eventSMQueue.set()
                self.eventLock.release()
                self.eventCommand.wait()





class guiInput():
    def __init__(self, commandQueue, eventCommand, eventSMQueue, eventLock, guiQueue):
        self.commandQueue = commandQueue
        self.eventCommand = eventCommand
        self.eventSMQueue = eventSMQueue
        self.eventLock = eventLock
        self.guiQueue = guiQueue

    def sendCommand(self, command):
        '''send a command to the simulator'''
        self.eventLock.acquire()
        self.eventCommand.clear()
        self.commandQueue.put(command)
        self.eventSMQueue.set()
        self.eventLock.release()
        self.eventCommand.wait()

    def getNextMessage(self):
        ''' waits for a message to be available in the queue and returns it '''
        while self.guiQueue.empty():
            pass
        return self.guiQueue.get()

    def getMessage(self):
        '''returns the first message in the queue, None if empty '''
        if not self.guiQueue.empty():
            return self.guiQueue.get()
        else:
            return None
            
        
    