import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
import os

import SimulationManager
import UserInputManager
import queue
import threading
import time

import carrierTabClass
import customerTabClass
import graphTabClass
import scenarioTabClass
import mapFrameClass
import simulationFrameClass




class mainWindow:

	def __init__(self, guiInput):
		self.guiInput = guiInput
		self.simulationStatus = 'PreSimulation'
		
		self.t1 = 0
		self.t2 = 0

		# main window
		self.root = tk.Tk()
		self.root.protocol('WM_DELETE_WINDOW', self.closeFunction)
		self.root.title('vrpSimu')
		self.root.minsize(1200,800)


		


		#
		# 	WINDOW CONTENT
		#

		mainPw = ttk.PanedWindow(orient='horizontal')
		simulationPw = ttk.PanedWindow(mainPw, orient='vertical')


		# Data notebook
		self.panelNoteBook = tk.ttk.Notebook(mainPw)

		self.carrierTab = carrierTabClass.carrierTab(self.panelNoteBook, self.guiInput, self)
		self.panelNoteBook.add(self.carrierTab, text='Carrier')

		self.customerTab = customerTabClass.customerTab(self.panelNoteBook, self.guiInput, self)
		self.panelNoteBook.add(self.customerTab, text= 'Customer')

		self.graphTab = graphTabClass.graphTab(self.panelNoteBook, self.guiInput, self)
		self.panelNoteBook.add(self.graphTab, text='Graph')
		

		self.scenarioTab = scenarioTabClass.scenarioTab(self.panelNoteBook, self.guiInput, self)
		self.panelNoteBook.add(self.scenarioTab, text='Scenario')

		self.graphTab.setCarrierTab(self.carrierTab)
		self.carrierTab.setGraphTab(self.graphTab)


		

		self.lastPathUsed = os.getcwd()
		self.carrierTab.setLastPathUsed(self.lastPathUsed)
		self.customerTab.setLastPathUsed(self.lastPathUsed)
		self.graphTab.setLastPathUsed(self.lastPathUsed)
		self.scenarioTab.setLastPathUsed(self.lastPathUsed)


		# Request frame
		self.simulationFrame = tk.ttk.LabelFrame(simulationPw, text='Simulation')
		self.simuframe = simulationFrameClass.simulationFrame(self.simulationFrame, guiInput, self, self.carrierTab)
		self.simuframe.setCarrierTab(self.carrierTab)
		self.simuframe.setCustomerTab(self.customerTab)
		self.simuframe.setGraphTab(self.graphTab)
		self.simuframe.setScenarioTab(self.scenarioTab)

		# Map frame
		self.mapLabelFrame = tk.ttk.LabelFrame(simulationPw, text='Map', height = 200, padding=10)
		self.map = mapFrameClass.mapFrame(self.mapLabelFrame, guiInput, self, self.carrierTab, self.customerTab, self.graphTab, self.scenarioTab, self.simuframe)
		self.lastMapDisplayTime = 0


		self.customerTab.setMapFrame(self.map)
		self.graphTab.setMapFrame(self.map)
		self.scenarioTab.setMapFrame(self.map)
		self.carrierTab.setMapFrame(self.map)
		self.simuframe.setMapFrame(self.map)

		self.customerTab.setSimulationFrame(self.simuframe)
		self.graphTab.setSimulationFrame(self.simuframe)
		self.scenarioTab.setSimulationFrame(self.simuframe)
		self.carrierTab.setSimulationFrame(self.simuframe)


		# add and pack element
		mainPw.pack(fill='both', expand = True)

		mainPw.add(self.panelNoteBook)
		mainPw.add(simulationPw)

		simulationPw.add(self.mapLabelFrame)
		self.map.pack(fill='both', expand=True)
		simulationPw.add(self.simulationFrame)




		# main window bar menu
		self.menuBar = tk.Menu(self.root)

		# simulation menu
		self.simulationMenu = tk.Menu(self.menuBar, tearoff = 0)
		self.simulationMenu.add_command(label='play simulation',    command = self.simuframe.on_play)
		self.simulationMenu.add_command(label='pause simulation',    command = self.simuframe.on_pause)
		self.simulationMenu.add_command(label='stop simulation',     command = self.simuframe.on_stop)
		# self.simulationMenu.add_command(label='modify the solution')
		self.menuBar.add_cascade(label='Simulation', menu = self.simulationMenu)

		# help menu
		self.helpMenu = tk.Menu(self.menuBar, tearoff = 0)
		# self.menuBar.add_cascade(label='Help', menu=self.helpMenu)

		# file menu
		self.fileMenu = tk.Menu(self.menuBar, tearoff = 0)
		self.fileMenu.add_command(label='load Carrier',  command = self.carrierTab.on_loadCarrierButton)
		self.fileMenu.add_command(label='load Customer', command = self.customerTab.on_loadCustomerButton)
		self.fileMenu.add_command(label='load Graph',    command = self.graphTab.on_loadGraphButton)
		self.fileMenu.add_command(label='load Scenario', command = self.scenarioTab.on_loadScenarioButton)
		self.fileMenu.add_separator()
		self.fileMenu.add_command(label='save Scenario', command = self.scenarioTab.on_saveScenarioButton)
		self.fileMenu.add_command(label='save Last Solution', command = self.on_saveLastSolution)
		self.fileMenu.add_command(label='save All Solution', command = self.on_saveAllSolution)
		self.fileMenu.add_separator()
		self.fileMenu.add_command(label='load a solution file', command = self.on_loadSolution)
		
		self.menuBar.add_cascade(label='File', menu=self.fileMenu)

		self.root.config(menu=self.menuBar)
		self.root.config()

	def displayFocusOnRequest(self, requestId):
		self.customerTab.displayFocusOnRequest(requestId)
		self.scenarioTab.displayFocusOnRequest(requestId, seeRequest = True)

	def displayFocusOnNode(self, nodeId):
		self.graphTab.displayFocusOnNode(nodeId)

	def on_loadSolution(self):
		''' open a file dialog to get the name of the solution file to load
			and send a command to the simulator '''
		filename = tk.filedialog.askopenfilename(initialdir = self.lastPathUsed,title = "Select solution file",filetypes = (("json files","*.json"),("all files","*.*")))
		if filename != () and filename != '':
			self.guiInput.sendCommand('loadNewSolution '+filename)
			self.setLastPathUsed(os.path.dirname(filename))	

	def on_saveLastSolution(self):
		''' open a file dialog to retrieve the name of the file to save
		    and then send a command to the simulator to save the last solution in this file'''
		filename = tk.filedialog.asksaveasfilename(initialdir = self.lastPathUsed, title = 'Save last solution', filetypes = (("json files","*.json"),("all files","*.*")))
		if filename != () and filename != '':
			self.guiInput.sendCommand('saveLastSolution {}'.format(filename))
			self.setLastPathUsed(os.path.dirname(filename))

	def on_saveAllSolution(self):
		''' open a file dialog to retrieve the name of the file to save
		    and then send a command to the simulator to save all the solution in this file'''
		filename = tk.filedialog.asksaveasfilename(initialdir = self.lastPathUsed, title = 'Save all solution', filetypes = (("json files","*.json"),("all files","*.*")))
		if filename != () and filename != '':
			self.guiInput.sendCommand('saveSolutions {}'.format(filename))
			self.setLastPathUsed(os.path.dirname(filename))

	def onSaveLastSolutionInClick(self, nodeId):
		pass

	def setLastPathUsed(self, path):
		self.lastPathUsed = path
		self.carrierTab.setLastPathUsed(path)
		self.customerTab.setLastPathUsed(path)
		self.graphTab.setLastPathUsed(path)
		self.scenarioTab.setLastPathUsed(path)

	def start(self):
		self.root.after(2000, self.loopFunction)
		self.root.mainloop()
		self.root.quit()

	def closeFunction(self):
		if self.simulationStatus == 'OfflineEnd':
			self.guiInput.sendCommand('sendAll')
			self.guiInput.sendCommand('startOnlineSimulation')
		time.sleep(5)
		self.guiInput.sendCommand('stopSimulation')
		self.guiInput.sendCommand('close')
		self.root.destroy()

	def updateStatus(self, newStatus):
		self.simulationStatus = newStatus
		self.simuframe.updateStatus(newStatus)
		self.map.updateStatus(newStatus)
		self.carrierTab.updateStatus(newStatus)
		self.customerTab.updateStatus(newStatus)
		self.graphTab.updateStatus(newStatus)
		self.scenarioTab.updateStatus(newStatus)

	def sendAllData(self):
		self.scenarioTab.sendComputationTime()
		self.scenarioTab.sendOfflineTime()
		self.guiInput.sendCommand('sendAll')

	def sendComputationTime(self):
		self.scenarioTab.sendComputationTime()

	def sendCommand(self, command):
		self.eventLock.acquire()
		self.eventCommand.clear()
		self.commandQueue.put(command)
		self.eventSMQueue.set()
		self.eventLock.release()
		self.eventCommand.wait()


	def canvasCount(self, arg=1):
		pass


	def loopFunction(self):
		simulatorMsg = self.guiInput.getMessage()
		while simulatorMsg != None:

			msgType = simulatorMsg[0]
			msgBody = simulatorMsg[1]
			

			if msgType == 'error':
				tk.messagebox.showerror('Error', msgBody)

			# Loading instance data messages
			elif msgType == 'carrierData':
				if self.simulationStatus in ['PreSimulation']:
					self.carrierTab.displayData(msgBody)
					# self.simuframe.drawHeadingRectangle()
					self.map.displayInitialData()
				else:
					print('ERROR: GUI received carrier data from simulator, but the simulationStatus is ' + self.simulationStatus)

			elif msgType == 'customerData':
				if self.simulationStatus in ['PreSimulation']:
					self.customerTab.displayData(msgBody)
					self.simuframe.setHorizonSize(msgBody['HorizonSize'])
					self.map.displayInitialData()
					self.scenarioTab.setHorizonSize(msgBody['HorizonSize'])
				else:
					print('ERROR: GUI received Customer data from simulator, but the simulationStatus is ' + self.simulationStatus)

			elif msgType == 'graphData':
				if self.simulationStatus in ['PreSimulation']:
					self.graphTab.displayData(msgBody)
					self.map.displayInitialData()
				else:
					print('ERROR: GUI received graph data from simulator, but the simulationStatus is ' + self.simulationStatus)

			elif msgType == 'scenarioData':
				if self.simulationStatus in ['PreSimulation']:
					self.scenarioTab.displayData(msgBody)
					self.map.displayInitialData()
				else:
					print('ERROR: GUI received scenario data from simulator, but the simulationStatus is ' + self.simulationStatus)

			# update Status messages
			elif msgType == 'updateStatus':
				if self.simulationStatus in ['PreSimulation']:
					if msgBody == 'OfflineComputation':
						self.updateStatus(msgBody)
						self.simuframe.setOfflineTime(float(self.scenarioTab.getOfflineTime()))
					else:
						print('ERROR, GUI receive message updateStatus '+msgBody+' but the current gui status is PreSimulation')


				elif self.simulationStatus in ['OfflineComputation']:
					if msgBody == 'PreSimulation':
						self.updateStatus(msgBody)
					elif msgBody == 'OfflinePauseAsked':
						self.updateStatus(msgBody)
					elif msgBody == 'OfflineEnd':
						self.updateStatus(msgBody)
					else:
						print('ERROR, GUI receive message updateStatus '+msgBody+' but the current gui status is OfflineComputation')


				elif self.simulationStatus in ['OfflinePauseAsked']:
					if msgBody in ['PreSimulation', 'OfflinePause', 'OfflineEnd']:
						self.updateStatus(msgBody)
					else:
						print('ERROR, GUI receive message updateStatus '+msgBody+' but the current gui status is OfflinePauseAsked')


				elif self.simulationStatus in ['OfflinePause']:
					if msgBody in ['OfflineComputation', 'OfflineEnd', 'PostSimulation']:
						self.updateStatus(msgBody)
					else:
						print('ERROR, GUI receive message updateStatus '+msgBody+' but the current gui status is OfflinePause')


				elif self.simulationStatus in ['OfflineEnd']:
					if msgBody == 'OnlineComputation':
						self.updateStatus(msgBody)
						self.simuframe.setComputationTime(float(self.scenarioTab.getComputationTime()))
					elif msgBody == 'PreSimulation':
						self.updateStatus(msgBody)
					else:
						print('ERROR, GUI receive message updateStatus '+msgBody+' but the current gui status is OfflineEnd')


				elif self.simulationStatus in ['OnlineComputation']:
					if msgBody == 'OnlinePauseAsked':
						self.updateStatus(msgBody)
					elif msgBody == 'PostSimulation':
						self.updateStatus(msgBody)
					elif msgBody == 'PreSimulation':
						self.updateStatus(msgBody)
					else:
						print('ERROR, GUI receive message updateStatus '+msgBody+' but the current gui status is OnlineComputation')


				elif self.simulationStatus in ['OnlinePauseAsked']:
					if msgBody in ['OnlinePause', 'PostSimulation']:
						self.updateStatus(msgBody)
					else:
						print('ERROR, GUI receive message updateStatus '+msgBody+' but the current gui status is OnlinePause')


				elif self.simulationStatus in ['OnlinePause']:
					if msgBody == 'OnlineComputation':
						self.updateStatus(msgBody)
					else:
						print('ERROR, GUI receive message updateStatus '+msgBody+' but the current gui status is OnlinePauseAsked')


				elif self.simulationStatus in ['PostSimulation']:
					if msgBody == 'PreSimulation':
						self.updateStatus(msgBody)
					else:
						print('ERROR, GUI receive message updateStatus '+msgBody+' but the current gui status is PostSimulation')


			elif msgType == 'updateBestSolution':
				if self.simulationStatus in ['OfflineComputation', 'OfflinePauseAsked', 'OfflineEnd', 'OnlineComputation', 'OnlinePauseAsked', 'PostSimulation']:
					self.simuframe.newSolverSolution(msgBody)
					self.scenarioTab.newSolverSolution(msgBody)
				else:
					pass
					# No error message should be displayed, because a new solution can arrive on presimulation  i.e if we stop the simulation
					# print('ERROR, GUI received updateBestSolution message, but the current gui status is '+self.simulationStatus)

			elif msgType == 'newSolutionLoaded':
				if self.simulationStatus in ['OfflineComputation', 'OfflinePauseAsked', 'OfflineEnd', 'OnlineComputation', 'OnlinePauseAsked', 'PostSimulation']:
					print('GUI: newSolutionLoaded')
					self.simuframe.newSolverSolution(msgBody)
					self.scenarioTab.newSolverSolution(msgBody)
				else:
					pass


			elif msgType == 'acceptedRequest':
				if self.simulationStatus in ['OfflineComputation', 'OfflinePauseAsked', 'OnlineComputation', 'OnlinePauseAsked']:
					print('newAcceptedRequest : ' + str(msgBody))
					# self.scenarioTab.newAcceptedRequest(msgBody)
					# self.simuframe.newAcceptedRequest(msgBody)
				else:
					print('ERROR, GUI received acceptedRequest message, but the current gui status is ' + self.simulationStatus)

			elif msgType == 'startTimeOffline':
				# message announcing the start time of the offline simulation
				if self.simulationStatus in ['PreSimulation', 'OfflineComputation', 'OfflinePauseAsked', 'OfflineEnd']:
					self.simuframe.setStartTimeOffline(msgBody)
					self.scenarioTab.setStartTimeOffline(msgBody)
				else:
					print('ERROR, GUI received startTimeOffline message, but the current gui status is '+self.simulationStatus)

			elif msgType == 'startOfflinePause':
				# message announcing the start time of the offline pause
				if self.simulationStatus in ['OfflinePauseAsked']:
					self.simuframe.setStartOfflinePause(msgBody)
					self.scenarioTab.setStartOfflinePause(msgBody)
				else:
					print('ERROR, GUI received startOfflinePause message, but the current gui status is '+self.simulationStatus)

			elif msgType == 'endOfflinePause':
				# message announcing the end time of the offline pause
				if self.simulationStatus in ['OfflinePause']:
					self.simuframe.setEndOfflinePause(msgBody)
					self.scenarioTab.setEndOfflinePause(msgBody)
				else:
					print('ERROR, GUI received endOfflinePause message, but the current gui status is '+self.simulationStatus)

			elif msgType == 'startTimeOnline':
				# message announcing the start time of the online simulation
				if self.simulationStatus in ['OfflineEnd', 'OnlineComputation']:
					self.simuframe.setStartTimeOnline(msgBody)
					self.scenarioTab.setStartTimeOnline(msgBody)
				else:
					print('ERROR, GUI received startTimeOffline message, but the current gui status is '+self.simulationStatus)

			elif msgType == 'startOnlinePause':
				# message announcing the start time of the online pause
				if self.simulationStatus in ['OnlineComputation', 'OnlinePauseAsked']:
					self.simuframe.setStartOnlinePause(msgBody)
					self.scenarioTab.setStartOnlinePause(msgBody)
				else:
					print('ERROR, GUI received startOnlinePause message, but the current gui status is '+self.simulationStatus)

			elif msgType == 'endOnlinePause':
				# message announcing the end time of the online pause
				if self.simulationStatus in ['OnlinePause']:
					self.simuframe.setEndOnlinePause(msgBody)
					self.scenarioTab.setEndOnlinePause(msgBody)
				else:
					print('ERROR, GUI received endOfflinePause message, but the current gui status is '+self.simulationStatus)

			else:
				print('MESSAGE FROM THE SIMULATOR COULD NOT BE HANDLED:'+str(simulatorMsg))


			simulatorMsg = self.guiInput.getMessage()


		self.t1 = time.time()
		if self.t1 - self.t2 > 1:
			self.simuframe.displayLastSolution()

			self.scenarioTab.displayLastSolution()

			self.map.updateDisplay()
			self.t2 = time.time()


		self.simuframe.displayTime()


		self.root.after(50, self.loopFunction)





		


