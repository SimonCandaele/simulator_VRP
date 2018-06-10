import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
import Pmw
import os
import math
import copy

class customerTab(tk.Frame):
	def __init__(self, root, guiInput, mainroot):
		tk.Frame.__init__(self, root, bd=5)
		self.mainroot = mainroot
		self.pw = ttk.PanedWindow(self, orient = 'vertical')
		
		self.lastPathUsed = os.getcwd()
		self.loadCustomerButton = tk.Button(self , text = 'load CustomerFile', command = self.on_loadCustomerButton)
		self.loadCustomerButton.pack(side = 'top')
		
		self.guiInput = guiInput
		self.dataLoaded = False
		self.customerObj = None

		

		# labelFrame for the parameter
		self.lfParameter = tk.ttk.LabelFrame(self.pw, text='Parameters', padding = 5)
		self.pw.add(self.lfParameter)
		self.fieldFileName = Pmw.EntryField(self.lfParameter, labelpos='w', label_text = 'File', value='', entry_state='disabled')
		self.fieldTimeSlotNumber = Pmw.EntryField(self.lfParameter, labelpos='w', label_text='TimeSlots Number', value = '', entry_state='disabled')
		self.fieldHorizonSize = Pmw.EntryField(self.lfParameter, labelpos='w', label_text='Horizon Size', value = '', entry_state='disabled')
		self.fieldTUDuration = Pmw.EntryField(self.lfParameter, labelpos = 'w', label_text='Real TU duration', value = '', entry_state='disabled')

		
		self.fieldFileName.pack(fill='x', expand = 1, padx = 10, pady = 3)
		self.fieldTimeSlotNumber.pack(fill='x', expand = '1', padx=10, pady=3)
		self.fieldHorizonSize.pack(fill='x', expand = '1', padx=10, pady=3)
		self.fieldTUDuration.pack(fill='x', expand = '1', padx=10, pady=3)
		


		# labelFrame for the potential requests
		self.lfRequests = tk.ttk.LabelFrame(self.pw, text='Potential Requests', padding = 5)
		self.container1 = tk.Frame(self.lfRequests)
		self.treeRequest = ttk.Treeview(self.container1, selectmode = 'browse')
		self.scrollRequesty = ttk.Scrollbar(self.container1, orient='vertical', command=self.treeRequest.yview)
		self.scrollRequestx = ttk.Scrollbar(self.lfRequests, orient='horizontal', command=self.treeRequest.xview)
		self.treeRequest.config(yscrollcommand=self.scrollRequesty.set, xscrollcommand=self.scrollRequestx)
		self.treeRequest.bind('<Button-1>', self.on_treeRequestClick)

		self.treeRequest['show'] = 'headings'
		self.treeRequest['columns'] = ('1', '2', '3', '4', '5', '6', '7')
		columnHeading = ['RequestId', 'Node', 'Demand', 'ServiceDuration', 'TW start', 'TW end', 'TW type']
		self.treeRequestSortKey = (None,None)
		for i in range(7):
			self.treeRequest.column(str(i+1), width = 50, minwidth=75, stretch=True, anchor='c')
			self.treeRequest.heading(str(i+1), text=columnHeading[i])

		# labelFrame for the arrival Probability
		self.lfRequestsProb = tk.ttk.LabelFrame(self.pw, text='Arrival Probabilities', padding = 5)
		self.container2 = tk.Frame(self.lfRequestsProb)
		self.treeReqId = ttk.Treeview(self.container2, selectmode='browse')
		self.treeProb = ttk.Treeview(self.container2, selectmode = 'browse')
		self.scrollProby = ttk.Scrollbar(self.container2, orient='vertical', command=self.scrollbarProb)
		self.scrollProbx = ttk.Scrollbar(self.lfRequestsProb, orient='horizontal', command=self.treeProb.xview)
		self.treeProb.config(yscrollcommand=self.scrollwheelProb, xscrollcommand=self.scrollProbx)
		self.treeReqId.config(yscrollcommand=self.scrollwheelProb)
		self.treeReqId['columns'] = ('0')
		self.treeReqId.column('0', width=40)
		self.treeReqId.heading('0', text= 'ReqId')
		self.treeProbSortKey = (None, False)
		self.treeProb.bind('<Button-1>', self.on_treeProbClick)
		self.treeReqId.bind('<Button-1>', self.on_treeReqIdClick)

		self.treeProb['show'] = 'headings'
		self.treeReqId['show'] = 'headings'

		# pack and add
		self.pw.add(self.lfRequests)
		self.container1.pack(side='top', fill='both', expand= True)
		self.scrollRequesty.pack(side='left', fill='y')
		self.treeRequest.pack(side='left', fill='both', expand=True)
		self.scrollRequestx.pack(side='top', fill='x')

		self.pw.add(self.lfRequestsProb)
		self.container2.pack(side='top', fill='both', expand=True)
		self.scrollProby.pack(side='left', fill='y')
		self.treeReqId.pack(side='left', fill='y',)
		self.treeProb.pack(side='left', fill='both', expand=True)
		self.scrollProbx.pack(side='top', fill='x')




	def on_loadCustomerButton(self):
		'''Function called when loadCustomerButton is pressed'''
		self.customerFilename = tk.filedialog.askopenfilename(initialdir = self.lastPathUsed, title = "Select Customer file",filetypes = (("json files","*.json"),("all files","*.*")))
		if self.customerFilename != () and self.customerFilename != '':
			self.guiInput.sendCommand('loadCustomer '+self.customerFilename)
			self.mainroot.setLastPathUsed(os.path.dirname(self.customerFilename))

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


	def on_treeProbClick(self, event):
		'''synchronize the selections on the two treeviews of the travel times '''
		item = self.treeProb.identify('item', event.x, event.y)
		if item != '':
			itemId = self.treeReqId.identify_row(event.y)
			self.treeReqId.selection_set(itemId)
		elif self.treeProb.identify_region(event.x, event.y) == 'heading':
			colId = self.treeProb.identify_column(event.x)
			self.sortTreeProb(colId)

	def on_treeReqIdClick(self, event):
		'''synchronize the selections on the two treeviews of the travel times '''
		item = self.treeReqId.identify('item', event.x, event.y)
		if item != '':
			itemId = self.treeProb.identify_row(event.y)
			self.treeProb.selection_set(itemId)
		elif self.treeReqId.identify_region(event.x, event.y) == 'heading':
			colId = self.treeReqId.identify_column(event.x)
			self.sortTreeReqId(colId)

	def displayFocusOnNode(self, nodeId):
		self.treeRequest.selection_remove(self.treeRequest.selection())
		slct = []
		for child in self.treeRequest.get_children():
			if self.treeRequest.item(child)['values'][1] == nodeId:
				slct += [child]
		if len(slct) >= 1:
			self.treeRequest.selection_set(tuple(slct))
			self.treeRequest.see(slct[0])
				

	def displayFocusOnRequest(self, requestId):
		for child in self.treeRequest.get_children():
			if self.treeRequest.item(child)['values'][0] == requestId:
				self.treeRequest.selection_set(child)
				self.treeRequest.see(child)
				break
		ReqIndex = 0
		for child in self.treeReqId.get_children():
			if self.treeReqId.item(child)['values'][0] == requestId:
				ReqIndex = self.treeReqId.index(child)
				self.treeReqId.selection_set(child)
				self.treeRequest.see(child)
				break

		childs = self.treeProb.get_children()
		self.treeProb.selection_set(childs[ReqIndex])
		

	


	def displayData(self, customerObj):
		self.customerObj = customerObj


		self.fieldFileName.setentry(self.extractFileName(self.customerFilename))
		self.fieldTimeSlotNumber.setentry(customerObj['TimeSlotsNumber'])
		self.fieldHorizonSize.setentry(customerObj['HorizonSize'])
		self.fieldTUDuration.configure(label_text = 'TU Duration ('+str(customerObj['RealTimeUnit'])+')')
		self.fieldTUDuration.setentry(customerObj['RealDurationPerTimeUnit'])
		Pmw.alignlabels((self.fieldTimeSlotNumber, self.fieldHorizonSize, self.fieldTUDuration))

		self.loadCustomerButton.pack_configure(side='bottom')

		# labelFrame for the potential requests
		self.treeRequest.delete(*self.treeRequest.get_children())
		for req in self.customerObj['PotentialRequests']:
			val = [req['RequestId'], req['Node'], req['Demand'], req['ServiceDuration']]
			if req['TimeWindow']['TWType'] == 'absolute':
				val += [req['TimeWindow']['start'], req['TimeWindow']['end'], req['TimeWindow']['TWType']]
			elif req['TimeWindow']['TWType'] == 'relative':
				val += ['', '', req['TimeWindow']['TWType']]
			self.treeRequest.insert('', 'end', values=val)



		# labelFrame for the arrival Probability
		
		columnHeading = list(range(self.customerObj['TimeSlotsNumber']))
		self.treeProb['columns'] = tuple([str(i) for i in columnHeading])

		

		for i in columnHeading:
			self.treeProb.column(str(i), width = 20, minwidth=30, stretch=True, anchor='c')
			self.treeProb.heading(str(i), text = str(i))

		self.treeProb.delete(*self.treeProb.get_children())
		self.treeReqId.delete(*self.treeReqId.get_children())
		for req in self.customerObj['PotentialRequests']:
			val = req['ArrivalProbability']
			self.treeProb.insert('', 'end', values=val)
			self.treeReqId.insert('', 'end', values=req['RequestId'])

		self.pw.pack(fill='both', expand = True)

		self.dataLoaded = True

	def extractFileName(self, customerFilename):
		return customerFilename.split('/')[-1]

	def getCustomerObject(self):
		return self.customerObj

	def setMapFrame(self, mapFrame):
		self.mapFrame = mapFrame

	def setLastPathUsed(self, path):
		self.lastPathUsed = path

	def setSimulationFrame(self, simulationFrame):
		self.simulationFrame = simulationFrame

	def scrollbarProb(self, *args):
		self.treeProb.yview(*args)
		self.treeReqId.yview(*args)

	def scrollwheelProb(self, *args):
		self.scrollProby.set(*args)
		self.scrollbarProb('moveto', args[0])

	def sortTreeRequest(self, colId):
		''' sort the display of the potential requests '''
		lambdaF = None
		if colId == '#1':
			lambdaF = lambda k: k['RequestId']
			if self.treeRequestSortKey[0] != 'RequestId':
				self.treeRequestSortKey = ('RequestId', False)
			else:
				self.treeRequestSortKey = ('RequestId', not self.treeRequestSortKey[1])
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
			lambdaF = lambda k: k['TimeWindow']['TWType']
			if self.treeRequestSortKey[0] != 'TWType':
				self.treeRequestSortKey = ('TWType', False)
			else:
				self.treeRequestSortKey = ('TWType', not self.treeRequestSortKey[1])

		if lambdaF != None:
			# first copy the customer obj to avoid modifying it
			requests = copy.deepcopy(self.customerObj['PotentialRequests'])
			requests = sorted(requests, key = lambdaF, reverse = self.treeRequestSortKey[1])
			
			self.treeRequest.delete(*self.treeRequest.get_children())
			for req in requests:
				val = [req['RequestId'], req['Node'], req['Demand'], req['ServiceDuration']]
				if req['TimeWindow']['TWType'] == 'absolute':
					val += [req['TimeWindow']['start'], req['TimeWindow']['end'], req['TimeWindow']['TWType']]
				elif req['TimeWindow']['TWType'] == 'relative':
					val += ['', '', req['TimeWindow']['TWType']]
				self.treeRequest.insert('', 'end', values=val)

	def sortTreeProb(self, colId):
		''' sort the display of the potential requests '''
		# extract the timeslot number from the column Id
		timeSlotId = int(colId[1:])-1
		lambdaF = lambda k: k['ArrivalProbability'][timeSlotId]
		if self.treeProbSortKey[0] != timeSlotId:
			self.treeProbSortKey = (timeSlotId, True)
		else:
			self.treeProbSortKey = (timeSlotId, not self.treeProbSortKey[1])

		requests = copy.deepcopy(self.customerObj['PotentialRequests'])
		requests = sorted(requests, key = lambdaF, reverse = self.treeProbSortKey[1])
		self.treeProb.delete(*self.treeProb.get_children())
		self.treeReqId.delete(*self.treeReqId.get_children())
		for req in requests:
			val = req['ArrivalProbability']
			self.treeProb.insert('', 'end', values=val)
			self.treeReqId.insert('', 'end', values=req['RequestId'])	
		
	def sortTreeReqId(self, colId):
		self.treeProb.delete(*self.treeProb.get_children())
		self.treeReqId.delete(*self.treeReqId.get_children())
		if self.treeProbSortKey[0] == 'ReqId':
			self.treeProbSortKey = ('ReqId', not self.treeProbSortKey[1])
		else:
			self.treeProbSortKey = ('ReqId', True)

		if self.treeProbSortKey[1]:
			for req in self.customerObj['PotentialRequests']:
				val = req['ArrivalProbability']
				self.treeProb.insert('', 'end', values=val)
				self.treeReqId.insert('', 'end', values=req['RequestId'])
		else:
			for req in reversed(self.customerObj['PotentialRequests']):
				val = req['ArrivalProbability']
				self.treeProb.insert('', 'end', values=val)
				self.treeReqId.insert('', 'end', values=req['RequestId'])

	def isDataLoaded(self):
		return self.dataLoaded

	def updateStatus(self, newStatus):
		self.simulationStatus = newStatus
		if self.simulationStatus in ['PreSimulation']:
			self.loadCustomerButton.config(state = 'normal')

		elif self.simulationStatus in ['OfflineComputation']:
			self.loadCustomerButton.config(state = 'disabled')

		elif self.simulationStatus in ['OfflinePauseAsked']:
			self.loadCustomerButton.config(state = 'disabled')

		elif self.simulationStatus in ['OfflinePause']:
			self.loadCustomerButton.config(state = 'disabled')

		elif self.simulationStatus in ['OfflineEnd']:
			self.loadCustomerButton.config(state = 'disabled')

		elif self.simulationStatus in ['OnlineComputation']:
			self.loadCustomerButton.config(state = 'disabled')

		elif self.simulationStatus in ['OnlinePauseAsked']:
			self.loadCustomerButton.config(state = 'disabled')

		elif self.simulationStatus in ['OnlinePause']:
			self.loadCustomerButton.config(state = 'disabled')

		elif self.simulationStatus in ['PostSimulation']:
			self.loadCustomerButton.config(state = 'disabled')
			

