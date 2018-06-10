#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: simon candaele
"""

import queue
import threading

class ScriptManagerThread(threading.Thread):

    def __init__(self, commandQueue, eventCommandFinished, eventSMQueue, eventLock):
        threading.Thread.__init__(self)
        self.commandQueue = commandQueue
        self.eventCommandFinished = eventCommandFinished
        self.eventSMQueue = eventSMQueue
        self.eventLock = eventLock
        self.scriptFile = None

    def setScriptFile(self, scriptFilePath):
        self.scriptFilePath = scriptFilePath
        
    def run(self):
        try:
            with open(self.scriptFilePath) as scriptFile:
                # flag used to know if the command closed was in the file
                closeCommandInFile = False
                for command in scriptFile:

                    if command.split() == ['close']:
                        closeCommandInFile = True 

                    if len(command.split()) > 0:
                        print('--:', command)
                        # get the lock
                        self.eventLock.acquire()
                        self.eventCommandFinished.clear()
                        self.commandQueue.put(command.rstrip('\n'))
                        self.eventSMQueue.set()

                        # release the lock
                        self.eventLock.release()
                        self.eventCommandFinished.wait()

                # if the close command was not in the script
                # we add it so that the simulator process
                # can finish
                if not closeCommandInFile:
                    print('--:close')
                    self.eventLock.acquire()
                    self.eventCommandFinished.clear()
                    self.commandQueue.put('close')
                    self.eventSMQueue.set()

                    # release the lock
                    self.eventLock.release()
                    self.eventCommandFinished.wait()

        except IOError:
            print('cannot open the file', scriptFilePath)
