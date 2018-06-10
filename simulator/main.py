#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 12:48:58 2017

@author: simon candaele
"""
import SimulationManager
import UserInputManager
import gui
import ScriptManager
import queue
import threading
import sys

import cProfile, pstats, io
pr = cProfile.Profile()



if len(sys.argv) == 1:

	threads = []

	eventCommand = threading.Event()
	eventSMQueue = threading.Event()
	eventLock = threading.Lock()

	# create and launch the thread managing the user input
	commandQueue = queue.Queue(30)
	commandThread = UserInputManager.UIMthread(commandQueue, eventCommand, eventSMQueue, eventLock)
	commandThread.start()
	threads.append(commandThread)

	#create and launch the simulation manager thread
	simulationManagerThread = SimulationManager.SMthread(commandQueue, eventCommand, eventSMQueue, eventLock)
	simulationManagerThread.start()
	threads.append(simulationManagerThread)


	#wait all threads to end
	for t in threads:
	    t.join()
	print('Simulator Shutting Down')

else:
	if len(sys.argv) == 2 and sys.argv[1] == '--gui':
		threads = []

		eventCommand = threading.Event()
		eventSMQueue = threading.Event()
		guiQueue = queue.Queue()         # queue of message to the gui
		eventLock = threading.Lock()

		#create and launch the simulation manager thread
		commandQueue = queue.Queue(30)
		guiInput = UserInputManager.guiInput(commandQueue, eventCommand, eventSMQueue, eventLock, guiQueue)
		simulationManagerThread = SimulationManager.SMthread(commandQueue, eventCommand, eventSMQueue, eventLock)
		simulationManagerThread.setGuiQueue(guiQueue)
		simulationManagerThread.start()
		threads.append(simulationManagerThread)

		pr.enable()

		myMainWindow = gui.mainWindow(guiInput)
		myMainWindow.start()

		pr.disable()
		pr.dump_stats('/home/simon/Desktop/stats.txt')
		# s = io.StringIO()
		# sortby = 'cumulative'
		# ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
		# ps.print_stats()
		# print(s.getvalue())

		#wait all threads to end
		for t in threads:
		    t.join()
		print('Simulator Shutting Down')


	elif len(sys.argv) == 2 and sys.argv[1] == '--script':
		print('   Missing the path to the script')
	elif len(sys.argv) == 3 and sys.argv[1] == '--script':
		scriptFilePath = sys.argv[2]

		threads = []

		eventCommandFinished = threading.Event()
		eventSMQueue = threading.Event()
		eventLock = threading.Lock()

		# create and launch the thread managing the user input
		commandQueue = queue.Queue(30)
		commandThread = ScriptManager.ScriptManagerThread(commandQueue, eventCommandFinished, eventSMQueue, eventLock)
		commandThread.setScriptFile(scriptFilePath)
		commandThread.start()
		threads.append(commandThread)

		#create and launch the simulation manager thread
		simulationManagerThread = SimulationManager.SMthread(commandQueue, eventCommandFinished, eventSMQueue, eventLock)
		simulationManagerThread.setScriptMode(True)
		simulationManagerThread.start()
		threads.append(simulationManagerThread)

		#wait all threads to end
		for t in threads:
		    t.join()
		print('Simulator Shutting Down')

	else:
		print('   Incorrent arguments')


