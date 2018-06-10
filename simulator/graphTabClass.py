import tkinter as tk
import tkinter.ttk as ttk
import Pmw
import os
import math
import numpy
from sklearn.decomposition import PCA



class graphTab(tk.Frame):

	def __init__(self, root, guiInput, mainroot):
		tk.Frame.__init__(self, root, bd=5)
		self.mainroot = mainroot
		self.pw = ttk.PanedWindow(self, orient = 'vertical')
		

		self.lastPathUsed = os.getcwd()
		self.loadGraphButton = tk.Button(self, text = 'load GraphFile', command = self.on_loadGraphButton)
		#self.pw.add(self.loadGraphButton)
		self.loadGraphButton.pack( side   = 'top')
		self.guiInput = guiInput
		self.dataLoaded = False
		self.graphObj = None

		# labelFrame for the parameter
		self.lfParameter = tk.ttk.LabelFrame(self.pw, text='Parameters', padding = 5)
		self.pw.add(self.lfParameter)
		self.efFileName = Pmw.EntryField(self.lfParameter, labelpos='w', label_text = 'File', value='', entry_state='disabled')
		
		self.efFileName.pack(fill='x', expand = 1, padx = 10, pady = 3)

		self.lfNodes = tk.ttk.LabelFrame(self.pw, text='Nodes', padding=5)
		self.treeNode = ttk.Treeview(self.lfNodes, selectmode='browse')
		self.scrolly = ttk.Scrollbar(self.lfNodes, orient='vertical', command=self.treeNode.yview)
		self.treeNode.config(yscrollcommand=self.scrolly)
		self.treeNode.bind('<Button-1>', self.on_treeNodeClick)

		self.treeNode['show'] = 'headings'
		self.treeNode['columns'] = ('1','2','3')
		columnHeading = ['NodeId', 'MapCoord', 'NodeType']

		for i in range(3):
			self.treeNode.heading(str(i+1), text=columnHeading[i])

		self.treeNode.column('1', width= 50, anchor='c')
		self.treeNode.column('2', width= 70, anchor='c')
		self.treeNode.column('3', width=150, anchor='c')

		self.pw.add(self.lfNodes)
		self.scrolly.pack(side='left', fill='y')
		self.treeNode.pack(side='left', fill='both', expand=True)

		

	def on_loadGraphButton(self):
		'''Function called when loadGraphButton is pressed'''
		self.graphFilename = tk.filedialog.askopenfilename(initialdir = self.lastPathUsed,title = "Select graph file",filetypes = (("json files","*.json"),("all files","*.*")))
		if self.graphFilename != () and self.graphFilename != '':
			self.guiInput.sendCommand('loadGraph '+self.graphFilename)
			self.mainroot.setLastPathUsed(os.path.dirname(self.graphFilename))

	def on_treeNodeClick(self, event):
		region = self.treeNode.identify_region(event.x, event.y)
		if region == 'cell':
			treeRow = self.treeNode.identify_row(event.y)
			item = self.treeNode.item(treeRow)
			nodeId = item['values'][0]
			self.mapFrame.focusOnNode(nodeId)

	def extractFileName(self, filename):
		return filename.split('/')[-1]

	def displayData(self, graphObj):
		'''Display on the graph Tab the graph data contained in graphObj'''
		self.graphObj = graphObj

		self.efFileName.setentry(self.extractFileName(self.graphFilename))
		self.loadGraphButton.pack_configure(side='bottom')


		
		self.treeNode.delete(*self.treeNode.get_children())
		for req in self.graphObj['Nodes']:
			el = self.graphObj['Nodes'][req]
			val = [str(req), '', ', '.join(el['NodeType']) ]
			if el['MapCoord'] != None:
				val = [str(req), '('+str(el['MapCoord']['X'])+', '+str(el['MapCoord']['Y'])+')', ', '.join(el['NodeType'])]
			self.treeNode.insert('', 'end', values = val)

		self.pw.pack(fill='both', expand = True)

		self.mapCoordinateCheck()
		
		self.dataLoaded = True

	def displayFocusOnNode(self, nodeId):
		if nodeId != None and self.treeNode != None:
			for child in self.treeNode.get_children():
				if self.treeNode.item(child)['values'][0] == nodeId:
					self.treeNode.selection_set(child)
					self.treeNode.see(child)
					break

	def getGraphObject(self):
		return self.graphObj

	def getNodeMapCoord(self, nodeId):
		''' return a tuple (x, y) with the map coord of the node'''
		if str(nodeId) in self.graphObj['Nodes']:
			if 'MapCoord' in self.graphObj['Nodes'][str(nodeId)] and self.graphObj['Nodes'][str(nodeId)]['MapCoord'] != None:
				return (self.graphObj['Nodes'][str(nodeId)]['MapCoord']['X'], self.graphObj['Nodes'][str(nodeId)]['MapCoord']['Y'])
			else:
				return None
		else:
			return None

	def isDataLoaded(self):
		return self.dataLoaded

	def mapCoordinateCheck(self):
		computeCordinate = False
		if self.graphObj != None:
			if 'Nodes' in self.graphObj:
				someNode = next(iter(self.graphObj['Nodes'].values()))
				if 'MapCoord' not in someNode:
					computeCordinate = True
				elif someNode['MapCoord'] == None:
					computeCordinate = True
				elif 'X' not in someNode['MapCoord'] or 'Y' not in someNode['MapCoord']:
					computeCordinate = True
				elif 'X' in someNode['MapCoord'] and someNode['MapCoord']['X'] == None:
					computeCordinate = True
				elif 'Y' in someNode['MapCoord'] and someNode['MapCoord']['Y'] == None:
					computeCordinate = True

		matrix = self.carrierTab.getFictiveDistanceMatrix()
		if computeCordinate and matrix != None:
			matrix = numpy.matrix(matrix)
			pca = PCA(n_components = 2)
			matrix = pca.fit_transform(matrix)
			minX = matrix[:,0].min()
			minY = matrix[:,1].min()

			if minX < 0:
				matrix[:,0] = matrix[:,0] - minX
			if minY < 0:
				matrix[:,1] = matrix[:,1] - minY

			changeCoord = True
			for nodeId in self.graphObj['Nodes']:
				if int(nodeId) >= len(matrix):
					changeCoord = False
			if changeCoord:
				for nodeId in self.graphObj['Nodes']:
					self.graphObj['Nodes'][nodeId]['MapCoord'] = {'X':matrix[int(nodeId)][0], 'Y':matrix[int(nodeId)][1]}



	def setCarrierTab(self, carrierTab):
		self.carrierTab = carrierTab

	def setLastPathUsed(self, path):
		self.lastPathUsed = path

	def setMapFrame(self, mapFrame):
		self.mapFrame = mapFrame

	def setSimulationFrame(self, simulationFrame):
		self.simulationFrame = simulationFrame

	def updateStatus(self, newStatus):
		self.simulationStatus = newStatus
		if self.simulationStatus in ['PreSimulation']:
			self.loadGraphButton.config(state = 'normal')

		elif self.simulationStatus in ['OfflineComputation']:
			self.loadGraphButton.config(state = 'disabled')

		elif self.simulationStatus in ['OfflinePauseAsked']:
			self.loadGraphButton.config(state = 'disabled')

		elif self.simulationStatus in ['OfflinePause']:
			self.loadGraphButton.config(state = 'disabled')

		elif self.simulationStatus in ['OfflineEnd']:
			self.loadGraphButton.config(state = 'disabled')

		elif self.simulationStatus in ['OnlineComputation']:
			self.loadGraphButton.config(state = 'disabled')

		elif self.simulationStatus in ['OnlinePauseAsked']:
			self.loadGraphButton.config(state = 'disabled')

		elif self.simulationStatus in ['OnlinePause']:
			self.loadGraphButton.config(state = 'disabled')

		elif self.simulationStatus in ['PostSimulation']:
			self.loadGraphButton.config(state = 'disabled')
			