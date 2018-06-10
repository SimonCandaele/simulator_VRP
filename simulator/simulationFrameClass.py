import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import Pmw
import threading
import time
import sys

class simulationFrame(tk.Frame):

	def __init__(self, master, guiInput, mainroot, carrierTab):
		tk.Frame.__init__(self, master)

		# useful variables for the simulation
		self.guiInput = guiInput
		self.mainroot = mainroot
		self.carrierTab = carrierTab

		self.startTimeOffline = 0
		self.startTimeOnline = 0
		self.endOfflinePauseTime = 0
		self.endOnlinePauseTime = 0
		self.totalPauseTime = 0
		self.horizonSize = 0
		self.simulationStatus = 'PreSimulation'

		self.solutionsList = []
		self.solutionDisplayed = None
		self.displayFunctionBusy = False
		self.displayLock = threading.Lock()

		# Widgets declaration
		self.FrameButtons = tk.Frame(self, padx = 10, pady = 10)
		self.playButton = tk.Button(self.FrameButtons, text = 'play', command = self.on_play, state='normal')
		self.pauseButton = tk.Button(self.FrameButtons, text='pause', command = self.on_pause, state='disabled')
		self.stopButton = tk.Button(self.FrameButtons, text='stop', command = self.on_stop, state='disabled')
		self.sendDataButton = tk.Button(self.FrameButtons, text='send Data', command = self.on_sendData, state='normal')
		self.statusLabel = tk.Label(self.FrameButtons, text='Status : PreSimulation', width=30, borderwidth=2, relief='groove')
		self.currentTUvar = tk.StringVar()
		self.currentTUvar.set('Time Unit : ')
		self.currentTULabel = tk.Label(self.FrameButtons, width= 25, borderwidth=2, relief='groove', textvariable=self.currentTUvar)

		# canvas part for drawing the solution
		#self.lfCurrentSolution = ttk.LabelFrame(master, text = 'Current Solution', padding = 5)

		self.numberSolutionVar = tk.StringVar()
		self.numberSolutionVar.set('No solution yet')
		self.numberSolutionLabel = tk.Label(self.FrameButtons, width= 30, borderwidth=2, relief='groove', textvariable=self.numberSolutionVar)

		self.canvas = Pmw.ScrolledCanvas(self, borderframe = 1, hscrollmode = 'dynamic', vscrollmode='dynamic', canvasmargin = 5)
		self.canvas.config(background = 'white')
		self.canvas.interior().bind('<Button-1>', self.on_canvasClick)

		self.canvasObj = {}


		self.roadHeight = 70
		self.roadMargin = 5
		self.nodeWidth = 150


		self.colorScheduledRequest = '#9AE59A'  # request scheduled, not confirmed, red   
		#self.colorConfirmedRequest = '#FF944D'  # request confirmed for the future, orange
		self.colorCurrentNode      = '#34CB34'  # current node of the vehicle,      green flash
		self.colorPastNode              = '#9AE59A'  # node visited in the past,         green pale
		self.colorServedRequest = '#5EBF31'
		self.colorConfirmedRequest = '#EDA81E'  # confirmed for the future
		self.colorNoRequestNode = '#CCDDFF'

		# pack and display widget
		self.pack(side = 'top', expand=True, fill = 'both')
		self.FrameButtons.pack(side = 'top', anchor='nw')
		self.playButton.pack(side='left')
		self.pauseButton.pack(side='left')
		self.stopButton.pack(side='left')
		self.sendDataButton.pack(side='left')
		self.statusLabel.pack(side='left')
		self.currentTULabel.pack(side = 'left')

		
		self.numberSolutionLabel.pack(side='left')
		self.canvas.pack(side = 'top', anchor = 'nw', fill = 'both', expand = True)

	def updateStatus(self, newStatus):
		self.simulationStatus = newStatus
		if self.simulationStatus in ['PreSimulation']:
			self.clearCanvas()
			self.sendDataButton.config(state='normal')
			self.playButton.config(state='normal')
			self.pauseButton.config(state='disabled')
			self.stopButton.config(state='disabled')
			self.statusLabel.config(text='PreSimulation')
			self.currentTULabel.pack(side= 'left')
			self.numberSolutionVar.set('No solution yet')
			self.totalPauseTime = 0

		elif self.simulationStatus in ['OfflineComputation']:
			self.sendDataButton.config(state='disabled')
			self.playButton.config(state='disabled')
			self.pauseButton.config(state='normal')
			self.stopButton.config(state='normal')
			self.statusLabel.config(text='OfflineComputation')
			self.currentTULabel.pack(side='left')

		elif self.simulationStatus in ['OfflinePauseAsked']:
			self.sendDataButton.config(state='disabled')
			self.playButton.config(state='disabled')
			self.pauseButton.config(state='disabled')
			self.stopButton.config(state='normal')
			self.statusLabel.config(text='OfflinePauseAsked')
			self.currentTULabel.pack(side='left')

		elif self.simulationStatus in ['OfflinePause']:
			self.sendDataButton.config(state='disabled')
			self.playButton.config(state='normal')
			self.pauseButton.config(state='disabled')
			self.stopButton.config(state='normal')
			self.statusLabel.config(text='OfflinePause')
			self.currentTULabel.pack(side='left')

		elif self.simulationStatus in ['OfflineEnd']:
			self.sendDataButton.config(state='disabled')
			self.playButton.config(state='normal')
			self.pauseButton.config(state='disabled')
			self.stopButton.config(state='normal')
			self.statusLabel.config(text='OfflineEnd')
			self.currentTULabel.pack(side='left')
			self.totalPauseTime = 0

		elif self.simulationStatus in ['OnlineComputation']:
			self.sendDataButton.config(state='disabled')
			self.playButton.config(state='disabled')
			self.pauseButton.config(state='normal')
			self.stopButton.config(state='normal')
			self.statusLabel.config(text='OnlineComputation')
			self.currentTULabel.pack(side='left')

		elif self.simulationStatus in ['OnlinePauseAsked']:
			self.sendDataButton.config(state='disabled')
			self.playButton.config(state='disabled')
			self.pauseButton.config(state='disabled')
			self.stopButton.config(state='normal')
			self.statusLabel.config(text='OnlinePauseAsked')
			self.currentTULabel.pack(side='left')

		elif self.simulationStatus in ['OnlinePause']:
			self.sendDataButton.config(state='disabled')
			self.playButton.config(state='normal')
			self.pauseButton.config(state='disabled')
			self.stopButton.config(state='normal')
			self.statusLabel.config(text='OnlinePause')
			self.currentTULabel.pack(side='left')

		elif self.simulationStatus in ['PostSimulation']:
			self.sendDataButton.config(state='disabled')
			self.playButton.config(state='disabled')
			self.pauseButton.config(state='disabled')
			self.stopButton.config(state='normal')
			self.statusLabel.config(text='PostSimulation')
			self.currentTULabel.pack(side='left')
			self.totalPauseTime = 0

	def on_canvasClick(self, event):
		cx = self.canvas.canvasx(event.x)
		cy = self.canvas.canvasy(event.y)
		itemClicked = self.canvas.find_overlapping(cx, cy, cx, cy)

		# the click can not be on the heading
		if cx > self.nodeWidth :
			pass 
			# stopLoop = False
			# for roadId in self.canvasObj:
			# 	for roadNode in self.canvasObj[roadId]:
			# 		if roadNode['rectangle'] in itemClicked:
			# 			if 'RequestId' in roadNode:
			# 				self.mainroot.displayFocusOnRequest(roadNode['RequestId'])
			# 			if 'Node' in roadNode:
			# 				self.mainroot.displayFocusOnNode(roadNode['Node'])
			# 				self.mapFrame.focusOnNode(roadNode['Node'])
			# 			stopLoop = True
			# 			break
			# 	if stopLoop:
			# 		break
		# the click can be on the heading
		else:
			for roadId in self.canvasObj:
				if self.canvasObj[roadId]['heading']['rect1']['item'] in itemClicked:

					# add the status of the color rectangle to the data strucutre if not yet present
					if 'state' not in self.canvasObj[roadId]['heading']['rect2']:
						self.canvasObj[roadId]['heading']['rect2']['state'] = 'normal'

					# switch the status of the color rectangle
					if self.canvasObj[roadId]['heading']['rect2']['state'] == 'normal':
						self.canvasObj[roadId]['heading']['rect2']['state'] = 'hidden'
						self.canvas.itemconfig(self.canvasObj[roadId]['heading']['rect2']['item'], state='hidden')
						self.mapFrame.hideRoad(str(roadId))

					elif self.canvasObj[roadId]['heading']['rect2']['state'] == 'hidden':
						self.canvasObj[roadId]['heading']['rect2']['state'] = 'normal'
						self.canvas.itemconfig(self.canvasObj[roadId]['heading']['rect2']['item'], state='normal')
						self.mapFrame.showRoad(str(roadId))

					break


	def on_play(self):
		if self.simulationStatus == 'PreSimulation':
			self.guiInput.sendCommand('startOfflineSimulation')

		elif self.simulationStatus == 'OfflineEnd':
			self.mainroot.sendComputationTime()
			self.guiInput.sendCommand('startOnlineSimulation')

		elif self.simulationStatus in ['OnlinePauseAsked', 'OnlinePause', 'OfflinePauseAsked',  'OfflinePause']:
			self.guiInput.sendCommand('continue')			

		elif self.simulationStatus in ['']:
			print('GUI error: play button pressed while :'+self.simulationStatus)

	def on_pause(self):
		if self.simulationStatus in ['OnlineComputation', 'OfflineComputation']:
			self.guiInput.sendCommand('pause')
		else :
			print('GUI error: pause button pressed but the current status is ' + self.simulationStatus)

	def on_stop(self):
		if messagebox.askyesno("Stop Simulation", "End the current Simulation ?"):
			self.guiInput.sendCommand('stopSimulation')

	def on_sendData(self):
		self.mainroot.sendAllData()
		#self.guiInput.sendCommand('sendAll')

	def displayTime(self):
		if self.simulationStatus == 'PreSimulation':
			self.currentTUvar.set('Time Unit : ')

		elif self.simulationStatus in ['OfflineComputation', 'OfflinePauseAsked']:
			if self.startTimeOffline == 0:
				self.currentTUvar.set('starting soon')
			elif time.time() > self.endOfflinePauseTime:
				dif = time.time()-self.startTimeOffline-self.totalPauseTime
				if dif < 0:
					self.currentTUvar.set('Start in {:5.2f} s'.format(dif))
				elif dif > self.offlineTime:
					self.currentTUvar.set('{:15s} {:5.2f} s'.format('remaining time', 0))
				else:
					self.currentTUvar.set('{:15s} {:5.2f} s'.format('remaining time', self.offlineTime - (time.time()-self.startTimeOffline+self.totalPauseTime)))

		elif self.simulationStatus in ['OfflinePause']:
			self.currentTUvar.set('{:15s} {:5.2f} s'.format('remaining time', self.offlineTime - (min(self.startOfflinePauseTime,time.time())-self.startTimeOffline+self.totalPauseTime)))

		elif self.simulationStatus == 'OfflineEnd':
			self.currentTUvar.set('0')

		elif self.simulationStatus in ['OnlineComputation', 'OnlinePauseAsked']:
			if self.startTimeOnline == 0:
				return 0
			elif time.time() - self.startTimeOnline- self.totalPauseTime < 0 :
				self.currentTUvar.set('Start in {:5.2f} s'.format((time.time() - self.startTimeOnline)))
			elif time.time() > self.endOnlinePauseTime:
				self.currentTUvar.set('{:10s} {:5.2f} on {}'.format('Time Unit', (time.time() - self.startTimeOnline - self.totalPauseTime) / self.computationTime, self.horizonSize))

		elif self.simulationStatus in ['OnlinePause']:
			self.currentTUvar.set('{:10s} {:5.2f} on {}'.format('Time Unit', (min(self.startOnlinePauseTime,time.time()) - self.startTimeOnline - self.totalPauseTime) / self.computationTime, self.horizonSize))

		elif self.simulationStatus == 'PostSimulation':
			self.currentTUvar.set('{:10s} {:5.2f} on {}'.format('Time Unit', self.horizonSize, self.horizonSize))


	def newSolverSolution(self, newSolution):
		if self.canvas.winfo_manager() == '':
			self.canvas.pack(side = 'top', fill = 'both', expand = True)
		self.solutionsList += [newSolution]

	def setOfflineTime(self, offlineTime):
		self.offlineTime = offlineTime

	def setComputationTime(self, computationTime):
		self.computationTime = computationTime

	def setCarrierTab(self, carrierTab):
		self.carrierTab = carrierTab

	def setCustomerTab(self, customerTab):
		self.customerTab = customerTab

	def setGraphTab(self, graphTab):
		self.graphTab = graphTab

	def setScenarioTab(self, scenarioTab):
		self.scenarioTab = scenarioTab

	def setMapFrame(self, mapFrame):
		self.mapFrame = mapFrame

	def setHorizonSize(self, horizonSize):
		self.horizonSize = horizonSize

	def setStartTimeOffline(self, startTimeOffline):
		self.startTimeOffline = startTimeOffline

	def setStartOfflinePause(self, startOfflinePauseTime):
		self.startOfflinePauseTime = startOfflinePauseTime
		self.endOfflinePauseTime = sys.float_info.max

	def setEndOfflinePause(self, endOfflinePauseTime):
		self.endOfflinePauseTime = endOfflinePauseTime
		self.totalPauseTime += endOfflinePauseTime - self.startOfflinePauseTime

	def setStartTimeOnline(self, startTimeOnline):
		self.startTimeOnline = startTimeOnline

	def setStartOnlinePause(self, startOnlinePauseTime):
		self.startOnlinePauseTime = startOnlinePauseTime
		self.endOnlinePauseTime = sys.float_info.max

	def setEndOnlinePause(self, endOnlinePauseTime):
		self.endOnlinePauseTime = endOnlinePauseTime
		self.totalPauseTime += endOnlinePauseTime - self.startOnlinePauseTime



	def clearCanvas(self):
		self.canvas.delete('all')
		self.canvasObj = {}
		self.solutionsList = []
		self.solutionDisplayed = None
		self.displayFunctionBusy = False
		#self.pack_forget()

	def getCurrentTU(self):
		if self.simulationStatus in ['OfflineComputation', 'OfflinePause', 'OfflinePauseAsked', 'OfflineEnd']:
			return -1
		elif self.simulationStatus in ['OnlineComputation', 'OnlinePauseAsked']:
			if self.startTimeOnline != 0:
				return (time.time() - self.startTimeOnline - self.totalPauseTime)/self.computationTime
			else:
				return 0
		elif self.simulationStatus in ['OnlinePause']:
			return (min(self.startOnlinePauseTime,time.time()) - self.startTimeOnline - self.totalPauseTime)/self.computationTime
		elif self.simulationStatus in ['PostSimulation']:
			return self.horizonSize
		else:
			return -1

	def getLastSolution(self):
		if len(self.solutionsList) != 0:
			return (self.solutionsList[-1], len(self.solutionsList)-1 )
		else:
			return (None, None)

	def displayLastSolution(self):
		if len(self.solutionsList) > 0:

			# get the solution object and the nummer of this solution
			lastSolution = self.solutionsList[-1]
			solutionId   = len(self.solutionsList)-1

			self.displaySolution(lastSolution, solutionId)
			self.numberSolutionVar.set('Solution {:4d}   on {:4d} '.format(solutionId+1, len(self.solutionsList)))
		else:
			self.canvas.delete('all')
			self.canvasObj = {}

		self.canvas.resizescrollregion()

	def displaySolution(self, solution, solId):
		'''Display the solution on the simulation Frame canvas

		   solution contains a structure describing the solution
		   solId    contains the id of the solution to display'''
		currentTU = self.getCurrentTU()

		if solId != None:
			for r in solution['Routes']:

				roadId = str(r)
				roadLength = len(solution['Routes'][roadId])

				
				if roadId not in self.canvasObj:
					self.canvasObj[roadId] = {'nodes':[], 'line':{'item':None, 'coords':None}, 'heading':None}
				

				# manage the line
				line = self.canvasObj[roadId]['line']
				newCoord = (self.nodeWidth-self.roadMargin, int(roadId)*self.roadHeight+25, self.nodeWidth*(roadLength+1)-self.roadMargin, int(roadId)*self.roadHeight+25)

				# if a line is drawn change the coords if needed
				if line['item'] != None and line['coords'] != newCoord:
					self.canvasObj[roadId]['line']['coords'] = newCoord
					self.canvas.coords(line['item'], newCoord)
					#move the line to the bottom
					self.canvas.tag_lower(self.canvasObj[roadId]['line']['item'])

				# oterwhise create the line
				elif line['item'] == None:
					self.canvasObj[roadId]['line']['coords'] = newCoord
					self.canvasObj[roadId]['line']['item'] = self.canvas.create_line(newCoord)
					#move the line to the bottom
					self.canvas.tag_lower(self.canvasObj[roadId]['line']['item'])




				# heading of the road
				if self.canvasObj[roadId]['heading'] == None:
					self.canvasObj[roadId]['heading'] = {}
					bbox1 = (self.roadMargin, int(roadId)*self.roadHeight+self.roadMargin, self.nodeWidth-self.roadMargin, (int(roadId)+1)*self.roadHeight-self.roadMargin )
					bbox2 = (self.roadMargin+10, int(roadId)*self.roadHeight+50, self.nodeWidth-self.roadMargin-10, (int(roadId)+1)*self.roadHeight-self.roadMargin -10 )
					fill2 =  self.carrierTab.getColorOfVehicle(int(roadId))
					coordText = ( 50, int(roadId)*self.roadHeight+25)
					textText  = 'Vehicle '+roadId

					self.canvasObj[roadId]['heading']['rect1'] = {'coords' : bbox1, 'fill': 'grey80', 'tags' : ('Heading',)}
					self.canvasObj[roadId]['heading']['rect2'] = {'coords' : bbox2, 'fill': fill2,    'tags' : ('Heading',)}
					self.canvasObj[roadId]['heading']['text']  = {'coords' : coordText, 'text': textText, 'tags': ('Heading',)}

					self.canvasObj[roadId]['heading']['rect1']['item'] = self.canvas.create_rectangle(bbox1, fill ='grey80', tags=('Heading'))
					self.canvasObj[roadId]['heading']['text']['item']  = self.canvas.create_text(coordText, text = textText, tags = 'Heading')
					self.canvasObj[roadId]['heading']['rect2']['item'] = self.canvas.create_rectangle(bbox2, fill = fill2, tags=('Heading'))

				# for each element of the road
				for i, node in enumerate(self.canvasObj[roadId]['nodes']):

					# build the text that must be displayed

					if i < roadLength:
						curNode = solution['Routes'][roadId][i]
						curText = node['text']['text']
						newText = None
						arrival = curNode['ArrivalTime']
						departure = curNode['DepartureTime']
						if 'RequestId' in curNode:
							newText = 'Node: {}\nRequest: {}\n\nArrival  Departure\n{:7.0f}   {:7.0f}'.format(curNode['InstanceVertexID'], curNode['RequestId'], arrival, departure)
						else:
							newText = 'Node: {}\n\n\nArrival   Departure\n{:7.0f}   {:7.0f}'.format(curNode['InstanceVertexID'], arrival, departure )

						# update the displayed text if needed
						if curText != newText:
							node['text']['text'] = newText
							node['text']['state'] = 'normal'
							self.canvas.itemconfig(node['text']['item'], text=newText, state = 'normal')

						if node['text']['state'] == 'hidden':
							self.canvas.itemconfig(node['text']['item'], state = 'normal')


						# change the color of the rect if needed
						rectColor = node['rect']['fill']

						if currentTU < arrival and rectColor != self.colorScheduledRequest:
							node['rect']['fill'] = self.colorScheduledRequest
							node['rect']['state'] = 'normal'
							self.canvas.itemconfig(node['rect']['item'], fill = self.colorScheduledRequest, state = 'normal')

						elif arrival <= currentTU and rectColor != self.colorServedRequest:
							node['rect']['fill'] = self.colorServedRequest
							node['rect']['state'] = 'normal'
							self.canvas.itemconfig(node['rect']['item'], fill = self.colorServedRequest, state = 'normal')

						if node['rect']['state'] == 'hidden':
							node['rect']['state'] = 'normal'
							self.canvas.itemconfig(node['rect']['item'], state = 'normal')

					else:
						node['rect']['state'] = 'hidden'
						node['text']['state'] = 'hidden'
						self.canvas.itemconfig(node['rect']['item'], state = 'hidden')
						self.canvas.itemconfig(node['text']['item'], state = 'hidden')


				# if new rect must be created on the canvas
				length = len(self.canvasObj[roadId]['nodes'])
				for j, curNode in enumerate(solution['Routes'][roadId][length:]):
					i = j+length
					newText = None
					arrival = curNode['ArrivalTime']
					departure = curNode['DepartureTime']

					#create the rectangle
					x0 = (i+1)*self.nodeWidth + self.roadMargin
					y0 = int(roadId)*self.roadHeight+self.roadMargin
					x1 = (i+2)*self.nodeWidth - self.roadMargin
					y1 = (int(roadId)+1)*self.roadHeight-self.roadMargin

					newCanvasNode = {}

					if currentTU < arrival:
						newCanvasNode['rect'] = {'coords': (x0,y0,x1,y1), 'fill': self.colorScheduledRequest, 'state':'normal'}
						newCanvasNode['rect']['item'] = self.canvas.create_rectangle((x0,y0,x1,y1), fill = self.colorScheduledRequest, state = 'normal')

					elif arrival <= currentTU:
						newCanvasNode['rect'] = {'coords': (x0,y0,x1,y1), 'fill': self.colorServedRequest, 'state':'normal'}
						newCanvasNode['rect']['item'] = self.canvas.create_rectangle((x0,y0,x1,y1), fill = self.colorServedRequest, state = 'normal')

					#create the text
					if 'RequestId' in curNode:
						newText = 'Node: {}\nRequest: {}\n\nArrival  Departure\n{:7.0f}   {:7.0f}'.format(curNode['InstanceVertexID'], curNode['RequestId'], arrival, departure)
					else:
						newText = 'Node: {}\n\n\nArrival   Departure\n{:7.0f}   {:7.0f}'.format(curNode['InstanceVertexID'], arrival, departure )

					newCanvasNode['text'] = {'coords' : (x0+5, y0+5), 'text' : newText, 'anchor' : 'nw', 'state':'normal'}
					newCanvasNode['text']['item'] = self.canvas.create_text((x0+5, y0+5), text = newText, anchor = 'nw', state='normal', font=("TkDefaultFont", 8))

					# add the new element to the structure
					self.canvasObj[roadId]['nodes'] += [newCanvasNode]

				


