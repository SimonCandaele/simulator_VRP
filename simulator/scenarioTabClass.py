import tkinter as tk
import tkinter.ttk as ttk
import Pmw
import os
import math
import copy
import time
import sys


class scenarioTab(tk.Frame):

	def __init__(self, root, guiInput, mainroot):
		tk.Frame.__init__(self, root, bd=5)
		self.mainroot = mainroot

		# variable to measure time
		self.solverSolution = {}
		self.simulationStatus = 'PreSimulation'
		self.offlineTime = 1.0
		self.computationTime = 1.0
		self.horizonSize = 0

		self.startTimeOffline = 0
		self.startOfflinePauseTime = 0
		self.endOfflinePauseTime = 0

		self.startTimeOnline = 0
		self.startOnlinePauseTime = 0
		self.endOnlinePauseTime = 0

		self.totalPauseTime = 0

		self.lastTUdisplayed = None

		# color variables

		self.colorScheduledRequest  = '#9AE59A'     
		self.colorCurrentNode       = '#34CB34'  
		self.colorPastNode          = '#34CB34'  
		self.colorConfirmedRequest  = '#9AE59A'  
		self.colorRevealedNotInRoad = '#ffff66'  
		self.colorNoRequestNode     = '#CCDDFF'

		self.colorRevealed          = '#ffff66'
		self.colorScheduled         = '#9AE59A'
		self.colorBusy              = '#34CB34'
		self.colorVisited           = '#34CB34'
		self.colorNotVisited        = '#ff4d4d'


		
		# widgets

		self.FrameButtons = tk.Frame(self)

		self.loadScenarioButton = tk.Button(self.FrameButtons, text = 'load ScenarioFile', command = self.on_loadScenarioButton)
		self.generateScenarioButton = tk.Button(self.FrameButtons, text='Generate Scenario', command = self.on_generateScenarioButton)
		self.lastPathUsed = os.getcwd()
		

		self.loadScenarioButton.pack( side   = 'left')
		self.generateScenarioButton.pack(side='left')
		

		self.guiInput = guiInput

		self.pw = ttk.PanedWindow(self, orient = 'vertical')
		self.lfRequests = None

		self.treeRequest = None
		self.treeRequestSortKey = ('RequestId', False)
		self.currentReqIdFocus = None


		# labelFrame for the options
		self.lfOptions = tk.LabelFrame(self, text = 'Parameters')
		self.efFileName = Pmw.EntryField(self.lfOptions,labelpos='w', label_text = 'File', value='', entry_state='disabled')
		self.efOfflineTime = Pmw.EntryField(self.lfOptions, labelpos='w', label_text='Offline Time (second)', validate = { 'validator' : 'real',  'min':0, 'minstrict':True}, command = self.sendOfflineTime)
		self.efComputationTime = Pmw.EntryField(self.lfOptions, labelpos='w', label_text='Computation Time (second)', validate = {'validator':'real', 'min':0, 'minstrict':True}, command = self.sendComputationTime)
		self.efOfflineTime.setvalue('1')
		self.efComputationTime.setvalue('1')
		
		self.FrameButtons.pack(side='top', fill='x')
		self.lfOptions.pack(side = 'top', fill='x')
		self.pw.pack(fill='both', expand = True)
		self.efFileName.pack(side = 'top', anchor = 'nw', pady = 3, padx = 5, fill = 'x', expand = True)
		self.efOfflineTime.pack(side='top', anchor='nw', pady = 3, padx = 5, fill = 'x',  expand = True)
		self.efComputationTime.pack(side='top', anchor='nw', pady = 3, padx = 5, fill = 'x',  expand = True)
		Pmw.alignlabels((self.efFileName, self.efOfflineTime, self.efComputationTime))

		self.dataLoaded = False
		self.scenarioObj = None

	def on_addRequestButton(self):
		vehTypeComboBox = None
		numberEF = None
		def commandHandler(result):
			if result == 'OK':
				newRequest = {'TimeWindow':{}}
				newRequest['Demand'] = DemandCounter.get()
				newRequest['Node'] = NodeIdCounter.get()
				newRequest['RevealTime'] = RevealTimeCounter.get()
				newRequest['ServiceDuration'] = ServiceDurationCounter.get()
				newRequest['TimeWindow']['start'] = startCounter.get()
				newRequest['TimeWindow']['end'] = endCounter.get()

				self.guiInput.sendCommand('newRequest '+str(newRequest).replace("'",'"'))
				self.dialogAddRequests.deactivate(result)
			else:
				self.dialogAddRequests.deactivate(result)

		self.dialogAddRequests = Pmw.Dialog(self, buttons = ('OK', 'Cancel'), defaultbutton = 'OK', title = 'New Request', command = commandHandler)


		NodeIdCounter = Pmw.Counter(self.dialogAddRequests.interior(), labelpos = 'w',     label_text='NodeId          ', entryfield_value = 0, entryfield_validate = {'validator': 'integer', 'min' : 0})
		DemandCounter = Pmw.Counter(self.dialogAddRequests.interior(), labelpos = 'w',     label_text='Demand          ', entryfield_value = 0, entryfield_validate = {'validator': 'integer', 'min' : 0})
		ServiceDurationCounter = Pmw.Counter(self.dialogAddRequests.interior(), labelpos = 'w', label_text='Service Duration', entryfield_value = 0, entryfield_validate = {'validator': 'integer', 'min' : 0})
		startCounter = Pmw.Counter(self.dialogAddRequests.interior(), labelpos = 'w',      label_text='TW start        ', entryfield_value = 0, entryfield_validate = {'validator': 'integer', 'min' : 0})
		endCounter   = Pmw.Counter(self.dialogAddRequests.interior(), labelpos = 'w',      label_text='TW end          ', entryfield_value = 0, entryfield_validate = {'validator': 'integer', 'min' : 0})
		RevealTimeCounter = Pmw.Counter(self.dialogAddRequests.interior(), labelpos = 'w', label_text='Reveal Time     ', entryfield_value = 0, entryfield_validate = {'validator': 'integer', 'min' : -1})

		NodeIdCounter.pack(side = 'top')
		DemandCounter.pack(side = 'top')
		ServiceDurationCounter.pack(side = 'top')
		startCounter.pack(side = 'top')
		endCounter.pack(side = 'top')
		RevealTimeCounter.pack(side = 'top') 

		self.dialogAddRequests.withdraw()
		self.dialogAddRequests.activate(geometry = 'centerscreenalways')

	def on_loadScenarioButton(self):
		'''function called when loadScenarioButton is pressed'''
		self.scenarioFilename = tk.filedialog.askopenfilename(initialdir = self.lastPathUsed,title = "Select scenario file",filetypes = (("json files","*.json"),("all files","*.*")))
		if self.scenarioFilename != () and self.scenarioFilename != '':
			self.guiInput.sendCommand('loadScenario '+self.scenarioFilename)
			self.mainroot.setLastPathUsed(os.path.dirname(self.scenarioFilename))

	def on_generateScenarioButton(self):
		'''function called when generateScenarioButton is pressed'''
		self.scenarioFilename = 'generated Scenario'
		self.guiInput.sendCommand('generateScenario --ot '+self.efOfflineTime.get()+ ' --ct '+self.efComputationTime.get())
		self.guiInput.sendCommand('sendScenarioToGUI')

	def on_saveScenarioButton(self):
		''' open a file dialog to save the scenario file '''

		self.scenarioFilename = tk.filedialog.asksaveasfilename(initialdir = self.lastPathUsed, title = 'Save scenario File', filetypes = (("json files","*.json"),("all files","*.*")))
		if self.scenarioFilename != () and self.scenarioFilename != '':
			self.guiInput.sendCommand('saveScenario {}'.format(self.scenarioFilename))

	def on_treeRequestClick(self, event):
		region = self.treeRequest.identify_region(event.x, event.y)
		if region == 'heading':
			colId = self.treeRequest.identify_column(event.x)
			self.sortTreeRequest(colId)
		if region == 'cell':
			treeRow = self.treeRequest.identify_row(event.y)
			item = self.treeRequest.item(treeRow)
			nodeId = item['values'][1]
			self.mapFrame.focusOnNode(nodeId)


	def extractFileName(self, customerFilename):
		'''extract the file name of the path '''
		return customerFilename.split('/')[-1]

	def displayFocusOnRequest(self, requestId, seeRequest = False):
		if requestId != None and self.treeRequest != None:
			# if requestId is not a list, we transform it into to avoid bug in for loop
			if type(requestId) == type(0):
				requestId = [requestId]
			slct = []
			for child in self.treeRequest.get_children():
				if self.treeRequest.item(child)['values'][0] in requestId:
					slct += [child]
					self.treeRequest.selection_set(child)
					if seeRequest:
						self.treeRequest.see(child)
					self.currentReqIdFocus = requestId
					
			self.treeRequest.selection_set(tuple(slct))
			if seeRequest:
				self.treeRequest.see(slct[0])

	def displayFocusOnNode(self, nodeId):
		''' Higlight all the treeview element associated with the given nodeId'''
		if self.treeRequest != None:
			self.treeRequest.selection_remove(self.treeRequest.selection())
			self.currentReqIdFocus = []
			slct = []
			for child in self.treeRequest.get_children():
				if self.treeRequest.item(child)['values'][1] == nodeId:
					slct += [child]
					self.currentReqIdFocus += [self.treeRequest.item(child)['values'][0]]
			if len(self.currentReqIdFocus) >= 1:
				self.treeRequest.selection_set(tuple(slct))
				self.treeRequest.see(slct[0])

	def displayData(self, scenarioObj):
		if 'Requests' in scenarioObj:
			self.scenarioObj = scenarioObj
			currentTU = self.getCurrentTU()
			if self.lfRequests != None:
				self.lfRequests.destroy()

			self.lfRequests = tk.ttk.LabelFrame(self.pw, text='Requests', padding = 5)
			self.container1 = tk.Frame(self.lfRequests)
			self.container2 = tk.Frame(self.lfRequests)
			self.addRequestButton = tk.Button(self.container2, text = 'New Request', state='normal', command = self.on_addRequestButton)

			self.treeRequest = ttk.Treeview(self.container1, selectmode = 'browse')
			self.scrollRequesty = ttk.Scrollbar(self.container1, orient='vertical', command=self.treeRequest.yview)
			self.scrollRequestx = ttk.Scrollbar(self.lfRequests, orient='horizontal', command=self.treeRequest.xview)
			self.treeRequest.config(yscrollcommand=self.scrollRequesty.set, xscrollcommand=self.scrollRequestx)

			self.treeRequest['show'] = 'headings'
			self.treeRequest['columns'] = ('1', '2', '3', '4', '5', '6', '7')
			columnHeading = ['RequestId', 'Node', 'Demand', 'ServiceDuration', 'start', 'end', 'Reveal Time']
			self.treeRequest.bind('<Button-1>', self.on_treeRequestClick)

			# get the currently focused item
			
			if self.treeRequest.focus() != '':
				self.currentReqIdFocus = self.treeRequest.item(self.treeRequest.focus())['values'][0]

			for i in range(7):
				self.treeRequest.column(str(i+1), width = 50, minwidth=75, stretch=True, anchor='c')
				self.treeRequest.heading(str(i+1), text=columnHeading[i])
			for req in self.scenarioObj['Requests']:
				val = [req['RequestId'], req['Node'], req['Demand'], req['ServiceDuration'], req['TimeWindow']['start'], req['TimeWindow']['end'], req['RevealTime']]

				reqStatus = self.getRequestStatus(req, currentTU)
				
				self.treeRequest.insert('', 'end', values=val, tags=(reqStatus, 'all'))

			if self.simulationStatus == 'PreSimulation':
				self.treeRequest.tag_configure('all',        background = 'white')
			else:
				self.treeRequest.tag_configure('Revealed',   background = self.colorRevealed)
				self.treeRequest.tag_configure('Scheduled',  background = self.colorScheduled)
				self.treeRequest.tag_configure('Busy',       background = self.colorBusy)
				self.treeRequest.tag_configure('Visited',    background = self.colorVisited)
				self.treeRequest.tag_configure('NotVisited', background = self.colorNotVisited)
			self.displayFocusOnRequest(self.currentReqIdFocus)

			self.treeChildren = self.treeRequest.get_children()
			self.treeItem     = []
			for child in self.treeChildren:
				self.treeItem += [self.treeRequest.item(child)]


			if 'ComputationTime' in scenarioObj:
				self.efComputationTime.setvalue(scenarioObj['ComputationTime'])
				self.computationTime = scenarioObj['ComputationTime']
			else:
				self.sendComputationTime()
			if 'OfflineTime' in scenarioObj:
				self.efOfflineTime.setvalue(scenarioObj['OfflineTime'])
				self.offlineTime = scenarioObj['OfflineTime']
			else:
				self.sendOfflineTime()


			# display widget
			self.pw.add(self.lfRequests)
			self.container2.pack(side= 'top', fill = 'x')
			self.addRequestButton.pack(side = 'top', anchor = 'nw')
			self.container1.pack(side='top', fill='both', expand= True)
			self.scrollRequesty.pack(side='left', fill='y')
			self.treeRequest.pack(side='left', fill='both', expand=True)
			self.scrollRequestx.pack(side='top', fill='x')

			self.efFileName.setentry(self.extractFileName(self.scenarioFilename))
			self.FrameButtons.pack_configure(side='bottom')

			self.dataLoaded = True



	def displayLastSolution(self, forceDisplay = False):
		''' 
			Arrange the content of the tab according to the last solution received
		    update the background color of the requests 
		'''

		if self.scenarioObj != None and self.simulationStatus in ['OfflineComputation', 'OfflinePauseAsked', 'OfflinePause', 'OfflineEnd', 'OnlineComputation', 'OnlinePauseAsked', 'OnlinePause', 'PostSimulation']:
			currentTU = self.getCurrentTU()

			if self.lastTUdisplayed != currentTU or forceDisplay:
				self.lastTUdisplayed = currentTU
				# keep track of the tag modified
				tagToConfigure = set({})

				for idx, child in enumerate(self.treeChildren):
					item = self.treeItem[idx]
					itemTags = item['tags']
					newTag = self.getTreeChildStatus(item['values'], currentTU)

					if newTag not in itemTags:
						self.treeRequest.item(child, tags = newTag)
						tagToConfigure.add(newTag)

				if 'Revealed' in tagToConfigure:
					self.treeRequest.tag_configure('Revealed', background=self.colorRevealed)
				if 'Scheduled' in tagToConfigure:
					self.treeRequest.tag_configure('Scheduled', background=self.colorScheduled)
				if 'Busy' in tagToConfigure:
					self.treeRequest.tag_configure('Busy', background=self.colorBusy)
				if 'Visited' in tagToConfigure:
					self.treeRequest.tag_configure('Visited', background=self.colorVisited)
				if 'NotVisited' in tagToConfigure:
					self.treeRequest.tag_configure('NotVisited', background=self.colorNotVisited)
			

	def resetDisplay(self):
		self.displayData(self.scenarioObj)



	def getCurrentTU(self):
		if self.simulationStatus in ['OfflineComputation', 'OfflinePause', 'OfflinePauseAsked']:
			if self.offlineTime > 0:
				calc = ((time.time() - self.startTimeOffline - self.totalPauseTime)/self.offlineTime) -1
				return min(calc, 0)
			elif time.time() - self.startTimeOffline - self.totalPauseTime > 0:
				return 0
			else:
				return -1;

		elif self.simulationStatus in ['OfflineEnd']:
			return 0
		elif self.simulationStatus in ['OfflineEnd']:
			return 0
		elif self.simulationStatus in ['OnlineComputation', 'OnlinePauseAsked']:
			if self.startTimeOnline != 0:
				return (time.time() - self.startTimeOnline - self.totalPauseTime)/self.computationTime
			else:
				return 0
		elif self.simulationStatus in ['OnlinePause']:
			return (min(self.startOnlinePauseTime, time.time()) - self.startTimeOnline - self.totalPauseTime)/self.computationTime
		elif self.simulationStatus in ['PostSimulation']:
			return self.horizonSize
		else:
			return -1

	def getOfflineTime(self):
		return self.efOfflineTime.get()

	def getComputationTime(self):
		return self.efComputationTime.get()

	def getRequestStatus(self, request, currentTU):
			if self.simulationStatus in ['OfflineComputation', 'OfflinePause', 'OfflinePauseAsked', 'OfflineEnd', 'OnlineComputation', 'OnlinePauseAsked', 'OnlinePause', 'PostSimulation']:
				if currentTU < request['RevealTime'] or currentTU < -1:
					return 'NotRevealed'
				elif currentTU >= request['RevealTime']:
					if 'Routes' in self.solverSolution:
						for r in self.solverSolution['Routes']:
							road = self.solverSolution['Routes'][r]
							for node in road:
								if 'RequestId' in node and node['RequestId'] == request['RequestId']:
									if currentTU <= node['ArrivalTime']:
										return 'Scheduled'
									elif currentTU >= node['ArrivalTime'] and currentTU < node['DepartureTime']:
										return 'Busy'
									elif currentTU >= node['DepartureTime']:
										return 'Visited'
						if currentTU > request['TimeWindow']['end']:
							return 'NotVisited'
					return 'Revealed'

			elif self.simulationStatus == 'PreSimulation':
				return 'NotRevealed'
			else:
				print('ERROR: could not find the simulationStatus which is '+ str(self.simulationStatus))
				return 'NotRevealed'

	def getTreeChildStatus(self, values, currentTU):
		if currentTU < -1:
			return 'NotRevealed'
		# If the simulation is currently online
		if self.simulationStatus in ['OnlineComputation', 'OnlinePauseAsked', 'OnlinePause', 'PostSimulation']:
			if currentTU < values[6]:
				return 'NotRevealed'
			elif currentTU >= values[6]:
				if 'Routes' in self.solverSolution:
					for r in self.solverSolution['Routes']:
						road = self.solverSolution['Routes'][r]
						for node in road:
							if 'RequestId' in node and node['RequestId'] == values[0]:
								if currentTU <= node['ArrivalTime']:
									return 'Scheduled'
								elif currentTU >= node['ArrivalTime'] and currentTU < node['DepartureTime']:
									return 'Busy'
								elif currentTU >= node['DepartureTime']:
									return 'Visited'
					if currentTU > values[5]:
						return 'NotVisited'
				return 'Revealed'
		# If the simulation is currently offline
		elif self.simulationStatus in ['OfflineComputation', 'OfflinePause', 'OfflinePauseAsked','OfflineEnd']:
			if values[6] < 0:
				if 'Routes' in self.solverSolution:
					for r in self.solverSolution['Routes']:
						road = self.solverSolution['Routes'][r]
						for node in road:
							if 'RequestId' in node and node['RequestId'] == values[0]:
								return 'Scheduled'
				return 'Revealed'
			else:
				return 'NotRevealed'

		elif self.simulationStatus == 'PreSimulation':
			return 'NotRevealed'
		else:
			print('ERROR: could not find the simulationStatus which is '+ str(self.simulationStatus))
			return 'NotRevealed'

	def getScenarioObj(self):
		return self.scenarioObj

	def isDataLoaded(self):
		return self.dataLoaded

	def newAcceptedRequest(self, requestId):
		for req in self.scenarioObj['Requests']:
			if req['RequestId'] == requestId:
				req['Accepted'] = True

			if type(req['RequestId']) != type(requestId):
				print('!!!!!!!!!!!!!!! ==========> the types are not the same in function newAcceptedRequest')

	def newSolverSolution(self, msgBody):
		self.solverSolution = msgBody

	def sendComputationTime(self):
		self.computationTime = float(self.efComputationTime.getvalue())
		self.guiInput.sendCommand('setComputationTime '+self.efComputationTime.getvalue())

	def sendOfflineTime(self):
		self.offlineTime = float(self.efOfflineTime.getvalue())
		self.guiInput.sendCommand('setOfflineTime '+self.efOfflineTime.getvalue())


	def setOfflineTime(self, offlineTime):
		self.offlineTime = offlineTime
		self.efOfflineTime.setvalue(offlineTime)

	def setComputationTime(self, computationTime):
		self.computationTime = computationTime
		self.efComputationTime.setvalue(computationTime)

	def setHorizonSize(self, horizonSize):
		self.horizonSize = horizonSize

	def setLastPathUsed(self, path):
		self.lastPathUsed = path

	def setMapFrame(self, mapFrame):
		self.mapFrame = mapFrame

	def setSimulationFrame(self, simulationFrame):
		self.simulationFrame = simulationFrame

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

	def sortTreeRequest(self, colId):
		''' sort the display of the potential requests '''
		lambdaF = None
		currentTU = self.getCurrentTU()
		if colId == '#1':
			lambdaF = lambda k: k['RequestId']
			if self.treeRequestSortKey[0] != 'RequestId':
				self.treeRequestSortKey = ('RequestId', not self.treeRequestSortKey[1])
			else:
				self.treeRequestSortKey = ('RequestId', False)
		elif colId == '#2':
			lambdaF = lambda k: k['Node']
			if self.treeRequestSortKey[0] != 'Node':
				self.treeRequestSortKey = ('Node', False)
			else:
				self.treeRequestSortKey = ('Node', not self.treeRequestSortKey[1])
		elif colId == '#3':
			lambdaF = lambda k: k['Demand']
			if self.treeRequestSortKey[0] != 'Demand':
				self.treeRequestSortKey = ('Demand', False)
			else:
				self.treeRequestSortKey = ('Demand', not self.treeRequestSortKey[1])
		elif colId == '#4':
			lambdaF = lambda k: k['ServiceDuration']
			if self.treeRequestSortKey[0] != 'ServiceDuration':
				self.treeRequestSortKey = ('ServiceDuration', False)
			else:
				self.treeRequestSortKey = ('ServiceDuration', not self.treeRequestSortKey[1])
			sortKey = 'ServiceDuration'
		elif colId == '#5':
			lambdaF = lambda k: k['TimeWindow']['start']
			if self.treeRequestSortKey[0] != 'TWstart':
				self.treeRequestSortKey = ('TWstart', False)
			else:
				self.treeRequestSortKey = ('TWstart', not self.treeRequestSortKey[1])
		elif colId == '#6':
			lambdaF = lambda k: k['TimeWindow']['end']
			if self.treeRequestSortKey[0] != 'TWend':
				self.treeRequestSortKey = ('TWend', False)
			else:
				self.treeRequestSortKey = ('TWend', not self.treeRequestSortKey[1])
		elif colId == '#7':
			lambdaF = lambda k: k['RevealTime']
			if self.treeRequestSortKey[0] != 'RevealTime':
				self.treeRequestSortKey = ('RevealTime', False)
			else:
				self.treeRequestSortKey = ('RevealTime', not self.treeRequestSortKey[1])

		if lambdaF != None:

			if self.treeRequest.focus() != '':
				self.currentReqIdFocus = self.treeRequest.item(self.treeRequest.focus())['values'][0]

			# first copy the customer obj to avoid modifying it
			requests = copy.deepcopy(self.scenarioObj['Requests'])
			requests = sorted(requests, key = lambdaF, reverse = self.treeRequestSortKey[1])
			
			self.treeRequest.tag_configure('Revealed', background = 'white')
			self.treeRequest.delete(*self.treeRequest.get_children())
			for req in requests:
				val = [req['RequestId'], req['Node'], req['Demand'], req['ServiceDuration'], req['TimeWindow']['start'], req['TimeWindow']['end'], req['RevealTime']]
				
				self.treeRequest.insert('', 'end', values=val, tags=('all',))

			self.treeRequest.tag_configure('Revealed', background=self.colorRevealed)
			self.treeRequest.tag_configure('Scheduled', background=self.colorScheduled)
			self.treeRequest.tag_configure('Busy', background=self.colorBusy)
			self.treeRequest.tag_configure('Visited', background=self.colorVisited)
			self.treeRequest.tag_configure('NotVisited', background=self.colorNotVisited)
			self.displayFocusOnRequest(self.currentReqIdFocus)

			self.treeChildren = self.treeRequest.get_children()
			self.treeItem     = []
			for child in self.treeChildren:
				self.treeItem += [self.treeRequest.item(child)]

			self.displayLastSolution(forceDisplay = True)


	def updateStatus(self, newStatus):
		self.simulationStatus = newStatus
		if self.simulationStatus in ['PreSimulation']:
			self.loadScenarioButton.config(state = 'normal')
			self.generateScenarioButton.config(state = 'normal')
			self.efOfflineTime.configure(entry_state='normal')
			self.efComputationTime.configure(entry_state='normal')
			self.resetDisplay()
			self.solverSolution = {}
			self.totalPauseTime = 0

		elif self.simulationStatus in ['OfflineComputation']:
			self.loadScenarioButton.config(state = 'disabled')
			self.generateScenarioButton.config(state = 'disabled')
			self.efOfflineTime.configure(entry_state='disabled')
			self.efComputationTime.configure(entry_state='normal')

		elif self.simulationStatus in ['OfflinePauseAsked']:
			self.loadScenarioButton.config(state = 'disabled')
			self.generateScenarioButton.config(state = 'disabled')
			self.efOfflineTime.configure(entry_state='normal')
			self.efComputationTime.configure(entry_state='normal')

		elif self.simulationStatus in ['OfflinePause']:
			self.loadScenarioButton.config(state = 'disabled')
			self.generateScenarioButton.config(state = 'disabled')
			self.efOfflineTime.configure(entry_state='disabled')
			self.efComputationTime.configure(entry_state='normal')

		elif self.simulationStatus in ['OfflineEnd']:
			self.loadScenarioButton.config(state = 'disabled')
			self.generateScenarioButton.config(state = 'disabled')
			self.efOfflineTime.configure(entry_state='disabled')
			self.efComputationTime.configure(entry_state='normal')
			self.totalPauseTime = 0

		elif self.simulationStatus in ['OnlineComputation']:
			self.loadScenarioButton.config(state = 'disabled')
			self.generateScenarioButton.config(state = 'disabled')
			self.efOfflineTime.configure(entry_state='disabled')
			self.efComputationTime.configure(entry_state='disabled')

		elif self.simulationStatus in ['OnlinePauseAsked']:
			self.loadScenarioButton.config(state = 'disabled')
			self.generateScenarioButton.config(state = 'disabled')
			self.efOfflineTime.configure(entry_state='disabled')
			self.efComputationTime.configure(entry_state='disabled')

		elif self.simulationStatus in ['OnlinePause']:
			self.loadScenarioButton.config(state = 'disabled')
			self.generateScenarioButton.config(state = 'disabled')
			self.efOfflineTime.configure(entry_state='disabled')
			self.efComputationTime.configure(entry_state='disabled')

		elif self.simulationStatus in ['PostSimulation']:
			self.loadScenarioButton.config(state = 'disabled')
			self.generateScenarioButton.config(state = 'disabled')
			self.efOfflineTime.configure(entry_state='disabled')
			self.efComputationTime.configure(entry_state='disabled')
			self.totalPauseTime = 0		