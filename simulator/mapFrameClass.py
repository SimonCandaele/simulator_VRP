import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import Pmw
import threading
import time
import sys
import bisect

class mapFrame(tk.Frame):

	def __init__(self, master, guiInput, mainroot, carrierTab, customerTab, graphTab, scenarioTab, simulationFrame):
		tk.Frame.__init__(self, master)

		self.simulationStatus = 'PreSimulation'

		self.guiInput = guiInput
		self.mainroot = mainroot
		self.carrierTab = carrierTab
		self.customerTab = customerTab
		self.graphTab = graphTab
		self.scenarioTab = scenarioTab
		self.simuFrame = simulationFrame

		# Constants for drawing on the canvas
		self.zoom = 1
		self.zoomUsed = None
		self.lastDisplayFunction = self.displayLastSolution  # when zooming, the zoom change and called the previous displaying fuction
		self.previousSolutionDisplayed = None


		self.margin = 0
		self.circleRadius = 5


		self.colorDefault          = 'white'
		self.colorWaitingPoint     = 'white'
		self.colorDepot            = 'black'
		self.colorPossibleCustomer = 'white'
		self.colorNotRevealed      = 'grey50'  

		self.colorRevealed         = '#ffff66'   # pale orange
		self.colorScheduled        = '#9AE59A'   # pale green
		self.colorBusy             = '#34CB34'   # green
		self.colorPast             = '#34CB34'   # green
		self.colorRejected         = '#ff6666'   # red
		self.colorRoad = ['#e6194b', '#3cb44b', '#ffe119', '#0082c8', '#f58231', '#911eb4', '#46f0f0', '#f032e6	', '#d2f53c', '#fabebe', '#008080', '#e6beff', '#aa6e28', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000080']

		# widgets

		self.FrameButtons = tk.Frame(self, padx = 5, pady = 5)
		# self.showGraphButton = tk.Button(self.FrameButtons, text = 'Graph', command = self.on_showGraphButton, state='normal')
		# self.showCustomersButton = tk.Button(self.FrameButtons, text = 'Potential Customers', command = self.on_showCustomersButton, state = 'normal')
		# self.showScenarioButton = tk.Button(self.FrameButtons, text = 'Scenario', command = self.on_showScenarioButton, state = 'normal')
		# self.showSolutionButton = tk.Button(self.FrameButtons, text = 'Solution', command = self.on_showSolutionButton, state = 'normal')
		self.zoomPButton = tk.Button(self.FrameButtons, text = 'Zoom +', command = self.on_zoomP, state = 'normal')
		self.zoomMButton = tk.Button(self.FrameButtons, text = 'Zoom -', command = self.on_zoomM, state = 'normal')
		self.zoomEntry   = Pmw.EntryField(self.FrameButtons, value=self.zoom, entry_width = 10, validate = {'validator' : 'real', 'min':0, 'minstrict': 0}, command = self.on_zoomEntry )

		self.canvas = Pmw.ScrolledCanvas(self, borderframe = 1, hscrollmode = 'dynamic', vscrollmode='dynamic', canvasmargin = 8)

		# structure holding all the line on the canvas
		self.canvasLines = {}
		# stucture holding all the circle on the canvas
		self.canvasNodes = {}

		self.canvas.config(background = 'white')
		self.canvas.interior().bind('<Button-1>', self.on_canvasClick)


		self.FrameButtons.pack(side= 'top', anchor = 'nw', fill = 'x')
		# self.showGraphButton.pack(side='left')
		# self.showCustomersButton.pack(side = 'left')
		# self.showScenarioButton.pack(side = 'left')
		# self.showSolutionButton.pack(side = 'left')
		self.zoomMButton.pack(side = 'left')
		self.zoomEntry.pack(side = 'left')
		self.zoomPButton.pack(side= 'left')
		self.canvas.pack(side = 'top', anchor = 'nw', fill = 'both', expand = True)


	def on_canvasClick(self, event):
		cx = self.canvas.canvasx(event.x)
		cy = self.canvas.canvasy(event.y)
		itemClicked = self.canvas.find_overlapping(cx, cy, cx, cy)
		for item in itemClicked:
			itemtags = self.canvas.gettags(item)
			nodeId = None
			if 'node' in itemtags:
				for tag in itemtags:
					if tag[0] == 'n' and tag[1:].isdigit():
						nodeId = int(tag[1:])
				self.graphTab.displayFocusOnNode(nodeId)

				if self.canvas.itemcget('n'+str(nodeId), 'width') == '3.0':
					self.canvas.itemconfig('n'+str(nodeId), width = 1)
				else:
					self.canvas.itemconfig('n'+str(nodeId), width = 3)

			if 'PossibleCustomer' in itemtags:
				self.customerTab.displayFocusOnNode(nodeId)
			if 'Customer' in itemtags:
				self.scenarioTab.displayFocusOnNode(nodeId)


	def on_showCustomersButton(self):
		self.displayCustomers()

	def on_showGraphButton(self):
		self.displayGraph()

	def on_showScenarioButton(self):
		self.displayScenario()

	def on_showSolutionButton(self):
		self.displayLastSolution()

	def displayCustomers(self):
		'''Draw the customers on the map'''
		graphObj = self.graphTab.getGraphObject()
		customerObj = self.customerTab.getCustomerObject()

		if graphObj != None and customerObj != None:

			# build a set of nodeId with customer(s)
			nodesWithCust = set({})
			for req in customerObj['PotentialRequests']:
				nodesWithCust.add(str(req['Node']))

			# for each node in the graph object
			for nodeId in graphObj['Nodes']:
				node = graphObj['Nodes'][nodeId]

				if node['MapCoord'] != None:
					# define the parameter of the node
					(nx, ny, radius) = (node['MapCoord']['X']+self.margin, node['MapCoord']['Y']+self.margin, self.circleRadius)
					bbox = (nx*self.zoom-radius, ny*self.zoom-radius, nx*self.zoom+radius, ny*self.zoom+radius)
					tags = tuple(node['NodeType'] + ['node', 'n' + str(nodeId)])
					if nodeId in nodesWithCust:
						tags = tags + ('PossibleCustomer',)

					nodeFill = self.colorDefault
					if 'Depot' in tags:
						nodeFill = self.colorDepot
					elif 'PossibleCustomer' in tags:
						nodeFill = self.colorPossibleCustomer
					elif 'WaitingPoint' in tags:
						nodeFill = self.colorWaitingPoint


					# first time the node is draw on the canvas
					if str(nodeId) not in self.canvasNodes:
						self.canvasNodes[str(nodeId)] = {'coords' : bbox, 'tags': tags, 'state': 'hidden', 'fill' : nodeFill}
						self.canvasNodes[str(nodeId)]['item'] = self.canvas.create_oval(bbox, tags = tags, state = 'hidden', fill = nodeFill)
					# node already draw, change the parameter of object then
					else:
						oldbbox = self.canvasNodes[str(nodeId)]['coords']
						oldtags = self.canvasNodes[str(nodeId)]['tags']
						if oldbbox != bbox or oldtags != tags or nodeFill != self.canvasNodes[str(nodeId)]['fill']:

							self.canvasNodes[str(nodeId)]['tags']   = tags
							self.canvasNodes[str(nodeId)]['state']  = 'hidden'
							self.canvasNodes[str(nodeId)]['coords'] = bbox
							self.canvasNodes[str(nodeId)]['fill']   = nodeFill

							self.canvas.itemconfig(self.canvasNodes[str(nodeId)]['item'], tags = tags, state = 'hidden', fill = nodeFill)
							self.canvas.coords(self.canvasNodes[str(nodeId)]['item'], bbox)


			self.canvas.itemconfig('node', state = 'normal')
			self.canvas.resizescrollregion()
			self.zoomUsed = self.zoom

	def displayInitialData(self):
		
		self.canvas.delete('all')
		self.canvasLines = {}
		self.canvasNodes = {}


		if self.graphTab.isDataLoaded():
			if self.customerTab.isDataLoaded():
				if self.scenarioTab.isDataLoaded():
					self.displayScenario()
				else:
					self.displayCustomers()
			else:
				self.displayGraph()


	def displayGraph(self):
		''' Draw all the points in the graph on the canvas'''

		graphObj = self.graphTab.getGraphObject()
		if graphObj != None:

			for nodeId in graphObj['Nodes']:
				node = graphObj['Nodes'][nodeId]
				if node['MapCoord'] != None:
					(nx, ny, radius) = (node['MapCoord']['X']+self.margin, node['MapCoord']['Y']+self.margin, self.circleRadius)
					tags = tuple(node['NodeType'] + ['node', 'n' + str(nodeId)])
					bbox = (nx*self.zoom-radius, ny*self.zoom-radius, nx*self.zoom+radius, ny*self.zoom+radius)

					nodeFill = self.colorDefault
					if 'Depot' in tags:
						nodeFill = self.colorDepot
					elif 'WaitingPoint' in tags:
						nodeFill = self.colorWaitingPoint
					elif 'PossibleCustomer' in tags:
						nodeFill = self.colorPossibleCustomer

					if str(nodeId) not in self.canvasNodes:
						self.canvasNodes[str(nodeId)] = {'coords' : bbox, 'tags' : tags, 'fill' : nodeFill}
						self.canvasNodes[str(nodeId)]['item'] = self.canvas.create_oval(bbox, tags = tags, fill=nodeFill)
					else:
						oldbbox = self.canvasNodes[str(nodeId)]['coords']
						oldtags = self.canvasNodes[str(nodeId)]['tags']
						if oldbbox != bbox or oldtags != tags or nodeFill != self.canvasNodes[str(nodeId)]['fill']:

							self.canvasNodes[str(nodeId)]['tags']   = tags
							self.canvasNodes[str(nodeId)]['state']  = 'hidden'
							self.canvasNodes[str(nodeId)]['coords'] = bbox
							self.canvasNodes[str(nodeId)]['fill']   = nodeFill

							self.canvas.itemconfig(self.canvasNodes[str(nodeId)]['item'], tags = tags, state = 'hidden', fill = nodeFill)
							self.canvas.coords(self.canvasNodes[str(nodeId)]['item'], bbox)
							

		self.canvas.itemconfig('node', state = 'normal')
		self.canvas.resizescrollregion()
		self.zoomUsed = self.zoom


		self.lastDisplayFunction = self.displayGraph

	def displayLastSolution(self):
		''' display the solution'''

		(solution, solutionId) = self.simuFrame.getLastSolution()
		# if (solutionId != None and solutionId != self.previousSolutionDisplayed) or self.zoomUsed != self.zoom:
		self.displayLastSolutionWork(solution, solutionId)
			

		self.lastDisplayFunction = self.displayLastSolution

	def displayLastSolutionWork(self, solution, solutionId):
		''' True work of displaying last solution on canvas. Use this function to measure time with profiling '''
		currentTU   = self.simuFrame.getCurrentTU()
		graphObj    = self.graphTab.getGraphObject()
		scenarioObj = self.scenarioTab.getScenarioObj()

		nodeServed = set({})
		requestServed = set({})

		if self.zoom != self.zoomUsed and graphObj != None:
			# for each node in the graph object
			for nodeId in graphObj['Nodes']:
				node = graphObj['Nodes'][nodeId]

				if node['MapCoord'] != None:
					# define the parameter of the node
					(nx, ny, radius) = (node['MapCoord']['X']+self.margin, node['MapCoord']['Y']+self.margin, self.circleRadius)
					bbox = (nx*self.zoom-radius, ny*self.zoom-radius, nx*self.zoom+radius, ny*self.zoom+radius)

					oldbbox = self.canvasNodes[str(nodeId)]['coords']
					if oldbbox != bbox:
						self.canvasNodes[str(nodeId)]['coords'] = bbox
						self.canvas.coords(self.canvasNodes[str(nodeId)]['item'], bbox)


		if solution != None:
			for roadId in solution['Routes']:

				if str(roadId) not in self.canvasLines:
					# each road has two lines on the canvas: the past and the future
					self.canvasLines[str(roadId)] = [{'item':None, 'coords':None, 'state':'normal'}, {'item':None, 'coords':None, 'state':'normal'}]

				previousNode = None

				# the two list are used to build the coords of each roads
				oldRoadCoords = []
				newRoadCoords = []

				for rnId, rn in enumerate(solution['Routes'][roadId]):

					curId = str(rn['InstanceVertexID'])
					if previousNode != None:

						prevId = str(previousNode['InstanceVertexID'])
						(n1, n2) = (str(min(int(prevId), int(curId))), str(max(int(prevId), int(curId))))

						# change the color of the oval if necessary
						nodeIdCanvas = self.canvasNodes[curId]['item']
						nodeFill     = self.canvasNodes[curId]['fill']
						if currentTU < rn['ArrivalTime'] and nodeFill != str(self.colorScheduled):

							self.canvas.itemconfig(nodeIdCanvas, fill=self.colorScheduled)
							self.canvasNodes[curId]['fill'] = self.colorScheduled
						elif currentTU >= rn['ArrivalTime'] and currentTU < rn['DepartureTime'] and nodeFill != self.colorBusy:
							self.canvas.itemconfig(nodeIdCanvas, fill=self.colorBusy)
							self.canvasNodes[curId]['fill'] = self.colorBusy
						elif currentTU >= rn['DepartureTime'] and nodeFill != self.colorPast:
							self.canvas.itemconfig(nodeIdCanvas, fill=self.colorPast)
							self.canvasNodes[curId]['fill'] = self.colorPast

						# add the id of the current node to the set of node with a request accepted
						nodeServed.add(curId)

						if 'RequestId' in rn:
							requestServed.add(rn['RequestId'])

						# change the line between previous and current node if needed
						
	
					
					# for each node, we add it either to the past or the future road
					roadColor = self.carrierTab.getColorOfVehicle(roadId)
					x = (graphObj['Nodes'][curId]['MapCoord']['X']+self.margin)*self.zoom
					y = (graphObj['Nodes'][curId]['MapCoord']['Y']+self.margin)*self.zoom

					if rn['DepartureTime'] > currentTU:
						newRoadCoords += [x, y]
					elif rn['DepartureTime'] <= currentTU:
						oldRoadCoords += [x, y]
					
					previousNode = rn


				# to make the junction between old and newRoad
				oldRoadCoords += [newRoadCoords[0], newRoadCoords[1]]

				# compare the coords and redraw the road if necessary
				if oldRoadCoords != self.canvasLines[str(roadId)][0]['coords']:
					# at least two points
					if len(oldRoadCoords) >= 4:
						# something is already draw
						if self.canvasLines[str(roadId)][0]['item'] != None:
							self.canvas.coords(self.canvasLines[str(roadId)][0]['item'], tuple(oldRoadCoords))
						else: #create the line
							self.canvasLines[str(roadId)][0]['item'] = self.canvas.create_line(tuple(oldRoadCoords), fill = roadColor, width = 3, state = self.canvasLines[str(roadId)][0]['state'])
					else: # less than 4 points, no road to display
						if self.canvasLines[str(roadId)][0]['item'] != None:
							self.canvas.delete(self.canvasLines[str(roadId)][0]['item'])
						self.canvasLines[str(roadId)][0]['item'] = None
						self.canvasLines[str(roadId)][0]['coords'] = None


				if newRoadCoords != self.canvasLines[str(roadId)][1]['coords']:
					# at least two points
					if len(newRoadCoords) >= 4:
						# something is already draw
						if self.canvasLines[str(roadId)][1]['item'] != None:
							self.canvas.coords(self.canvasLines[str(roadId)][1]['item'], tuple(newRoadCoords))
						else: #create the line
							self.canvasLines[str(roadId)][1]['item'] = self.canvas.create_line(tuple(newRoadCoords), fill = roadColor, width = 1, state = self.canvasLines[str(roadId)][0]['state'])
					else: # less than 4 points, no road to display
						if self.canvasLines[str(roadId)][1]['item'] != None:
							self.canvas.delete(self.canvasLines[str(roadId)][1]['item'])
						self.canvasLines[str(roadId)][1]['item'] = None
						self.canvasLines[str(roadId)][1]['coords'] = None

		self.canvas.itemconfig('Depot', fill = self.colorDepot)
		if scenarioObj != None and 'Requests' in scenarioObj and currentTU > -1:
			
			nodeToConfigure = {}

			for request in scenarioObj['Requests']:
				curId = str(request['Node'])
				# for each request in the scenario, we check if the node has an accepted request
				# if not, we check the RevealTime, and Time window information to know
				# the color that should be displayed for this node
				if currentTU >= request['RevealTime'] and request['RequestId'] not in requestServed:
					# retrieve the id of the oval item on the canvas and the color
					nodeIdCanvas = self.canvasNodes[curId]['item']

					# if the request is not served
					if request['TimeWindow']['end'] <= currentTU and nodeIdCanvas not in nodeToConfigure:
						nodeToConfigure[nodeIdCanvas] = self.colorRejected
						self.canvasNodes[curId]['fill'] = self.colorRejected
						
					# if the request not accepted but could be later.
					# here, we don't check if the node is in nodeToConfigure because this color
					# has priority on the colorRecjected
					if request['TimeWindow']['end'] > currentTU:
						nodeToConfigure[nodeIdCanvas] = self.colorRevealed
						self.canvasNodes[curId]['fill'] = self.colorRevealed


			# now we loop on the node that must have a rejected or revealed color
			for node in nodeToConfigure:
				self.canvas.itemconfig(node, fill=nodeToConfigure[node])







		self.zoomUsed = self.zoom
		self.canvas.resizescrollregion()
		self.previousSolutionDisplayed = solutionId
			
	def displayScenario(self):
		'''Display the scenario'''
		graphObj = self.graphTab.getGraphObject()
		customerObj = self.customerTab.getCustomerObject()
		scenarioObj = self.scenarioTab.getScenarioObj()

		if graphObj != None and customerObj != None and scenarioObj != None:

			# build a set of nodeId with customer(s)
			nodesWithCust = set({})
			for req in customerObj['PotentialRequests']:
				nodesWithCust.add(str(req['Node']))

			# build a set of nodeId with request(s)
			nodesWithRequest = set({})
			for req in scenarioObj['Requests']:
				nodesWithRequest.add(str(req['Node']))


			# for each node in the graph object
			for nodeId in graphObj['Nodes']:
				node = graphObj['Nodes'][nodeId]

				if node['MapCoord'] != None:
					# define the parameter of the node
					(nx, ny, radius) = (node['MapCoord']['X']+self.margin, node['MapCoord']['Y']+self.margin, self.circleRadius)
					bbox = (nx*self.zoom-radius, ny*self.zoom-radius, nx*self.zoom+radius, ny*self.zoom+radius)
					tags = tuple(node['NodeType'] + ['node', 'n' + str(nodeId)])
					if nodeId in nodesWithCust:
						tags = tags + ('PossibleCustomer',)
					if nodeId in nodesWithRequest:
						tags = tags + ('Request',)

					nodeFill = self.colorDefault
					if 'Request' in tags:
						nodeFill = self.colorNotRevealed
					elif 'Depot' in tags:
						nodeFill = self.colorDepot
					

					# first time the node is draw on the canvas
					if str(nodeId) not in self.canvasNodes:
						self.canvasNodes[str(nodeId)] = {'coords': bbox, 'tags': tags, 'state': 'hidden', 'fill' : nodeFill}
						self.canvasNodes[str(nodeId)]['item'] = self.canvas.create_oval(bbox, tags = tags, state = 'hidden', fill = nodeFill)
					# node already draw, change the parameter of object then
					else:
						oldbbox = self.canvasNodes[str(nodeId)]['coords']
						oldtags = self.canvasNodes[str(nodeId)]['tags']

						if oldbbox != bbox or oldtags != tags or nodeFill != self.canvasNodes[str(nodeId)]['fill']:

							self.canvasNodes[str(nodeId)]['tags']   = tags
							self.canvasNodes[str(nodeId)]['state']  = 'hidden'
							self.canvasNodes[str(nodeId)]['coords'] = bbox
							self.canvasNodes[str(nodeId)]['fill']   = nodeFill

							self.canvas.itemconfig(self.canvasNodes[str(nodeId)]['item'], tags = tags, state = 'hidden', fill = nodeFill)
							self.canvas.coords(self.canvasNodes[str(nodeId)]['item'], bbox)

			self.canvas.itemconfig('node', state = 'normal')
			self.canvas.resizescrollregion()
			self.zoomUsed = self.zoom

		self.lastDisplayFunction = self.displayScenario

	def focusOnNode(self, nodeId):
		''' shortly highlight the node indicated in nodeId'''
		if type(nodeId) == type(0):
			nodeId = [nodeId]
			
		for node in nodeId:
			if self.canvas.itemcget('n'+str(node), 'width') == '3.0':
				self.canvas.itemconfig('n'+str(node), width = 1)
			else:
				self.canvas.itemconfig('n'+str(node), width = 3)

	def hideRoad(self, roadId):
		roadId = str(roadId)
		if roadId in self.canvasLines:
			self.canvasLines[roadId][0]['state'] = 'hidden'
			self.canvasLines[roadId][1]['state'] = 'hidden'
			self.canvas.itemconfig(self.canvasLines[roadId][0]['item'], state = 'hidden')
			self.canvas.itemconfig(self.canvasLines[roadId][1]['item'], state = 'hidden')
		else:
			self.canvasLines[roadId] = [{'item':None, 'coords':None, 'state':'hidden'}, {'item':None, 'coords':None, 'state': 'hidden'}]

	def showRoad(self, roadId):
		roadId = str(roadId)
		if roadId in self.canvasLines:
			self.canvasLines[roadId][0]['state'] = 'normal'
			self.canvasLines[roadId][1]['state'] = 'normal'
			self.canvas.itemconfig(self.canvasLines[roadId][0]['item'], state = 'normal')
			self.canvas.itemconfig(self.canvasLines[roadId][1]['item'], state = 'normal')
		else:
			self.canvasLines[roadId] = [{'item':None, 'coords':None, 'state':'normal'}, {'item':None, 'coords':None, 'state': 'normal'}]

	def updateDisplay(self):
		doUpdate = False
		if self.zoomUsed != self.zoom:
			doUpdate = True

		if self.simulationStatus not in ['PreSimulation']:
			self.displayLastSolution()

		if doUpdate:
			self.lastDisplayFunction()


	def updateStatus(self, newStatus):
		self.simulationStatus = newStatus
		if self.simulationStatus in ['PreSimulation']:
			self.canvas.delete('all')
			self.canvasLines = {}
			self.canvasNodes = {}
			self.displayInitialData()

		elif self.simulationStatus in ['OfflineComputation']:
			pass
		elif self.simulationStatus in ['OfflinePauseAsked']:
			pass
		elif self.simulationStatus in ['OfflinePause']:
			pass
		elif self.simulationStatus in ['OfflineEnd']:
			pass
		elif self.simulationStatus in ['OnlineComputation']:
			pass
		elif self.simulationStatus in ['OnlinePauseAsked']:
			pass
		elif self.simulationStatus in ['OnlinePause']:
			pass
		elif self.simulationStatus in ['PostSimulation']:
			pass

	def on_zoomEntry(self):
		newZoom = float(self.zoomEntry.getvalue())
		if newZoom > 0:
			self.zoom = newZoom
			self.lastDisplayFunction()
		else:
			self.zoomEntry.setvalue(self.zoom)
				
	def on_zoomP(self):
		if self.zoom >= 1:
			self.zoom += 1
		elif self.zoom < 1:
			self.zoom = min(1, self.zoom * 4 / 3)
		self.zoomEntry.setvalue(self.zoom)
		self.lastDisplayFunction()


	def on_zoomM(self):
		if self.zoom > 1:
			self.zoom = max(1, self.zoom-1)
		elif self.zoom <= 1:
			self.zoom = self.zoom * 0.75
		self.zoomEntry.setvalue(self.zoom)
		self.lastDisplayFunction()