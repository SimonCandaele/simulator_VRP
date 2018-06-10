import tkinter as tk
import tkinter.ttk as ttk
import Pmw
import os
import math
import random
import copy


class carrierTab(tk.Frame):

	def __init__(self, root, guiInput, mainroot):
		tk.Frame.__init__(self, root, bd=5)
		self.mainroot = mainroot
		self.pw = ttk.PanedWindow(self, orient = 'vertical')
		#self.pw.pack(fill='both', expand = True)

		self.lastPathUsed = os.getcwd()
		self.loadCarrierButton = tk.Button(self, text = 'load CarrierFile', command = self.on_loadCarrierButton)
		self.loadCarrierButton.pack( side   = 'top')
		self.guiInput = guiInput
		self.carrierMatrix = None
		self.dataLoaded = False
		self.carrierObj = None

		self.colors = ['#1a1aff', '#00b300', '#00cccc', '#996600', '#992600', '#990033', '#ff4d88', '#9933ff', '#7a7a52', '#b3b300', '#666600']

		# labelFrame for the parameter
		self.lfParameter = tk.ttk.LabelFrame(self.pw, text='Parameters', padding = 5)
		self.pw.add(self.lfParameter, weight = 1)
		self.efFileName = Pmw.EntryField(self.lfParameter, labelpos='w', label_text = 'File', value='', entry_state='disabled')
		self.efTimeSlotNumber = Pmw.EntryField(self.lfParameter, labelpos='w', label_text='TimeSlots Number', value = '', entry_state='disabled')
		self.efTravelTimeUnit = Pmw.EntryField(self.lfParameter, labelpos='w', label_text='Travel Time Unit', value = '', entry_state='disabled')
		

		
		self.efFileName.pack(fill='x', expand = 1, padx = 10, pady = 3)
		self.efTimeSlotNumber.pack(fill='x', expand = '1', padx=10, pady=3)
		self.efTravelTimeUnit.pack(fill='x', expand = '1', padx=10, pady=3)
		

		# labelFrame for the vehicle types
		self.lfVehicleType = tk.ttk.LabelFrame(self.pw, text='Vehicle Types', padding = 5)
		self.pw.add(self.lfVehicleType, weight = 1)
		self.treeVehicleType = ttk.Treeview(self.lfVehicleType)
		self.scrollbarVehicleType = ttk.Scrollbar(self.lfVehicleType, orient='vertical', command = self.treeVehicleType.yview)
		self.treeVehicleType.config(yscrollcommand = self.scrollbarVehicleType.set)
		self.treeVehicleType['show'] = 'headings'
		self.treeVehicleType['columns'] = ('0', '1')
		self.treeVehicleType.column('0', width=100, anchor='c')
		self.treeVehicleType.column('1', width=100, anchor='c')
		self.treeVehicleType.heading('0', text='VehicleType')
		self.treeVehicleType.heading('1', text='Capacity')

		# labelFrame for the vehicle fleet
		self.lfVehicleFleet = tk.ttk.LabelFrame(self.pw, text='Vehicle fleet', padding = 5)
		self.pw.add(self.lfVehicleFleet, weight = 4)
		self.frameButtonsFleet = tk.Frame(self.lfVehicleFleet)
		self.frameTreeFleet = tk.Frame(self.lfVehicleFleet)

		self.addVehicleButton = tk.Button(self.frameButtonsFleet, text = 'Add Vehicles', state='normal', command = self.on_addVehicleButton)
		self.deleteFleetButton = tk.Button(self.frameButtonsFleet, text = 'delete Fleet', state = 'normal', command = self.on_deleteFleetButton)

		self.treeFleet = ttk.Treeview(self.frameTreeFleet)
		self.scrollbarFleet = ttk.Scrollbar(self.frameTreeFleet, orient='vertical', command = self.treeFleet.yview)
		self.treeFleet.config(yscrollcommand = self.scrollbarFleet.set)
		self.treeFleet['show'] = 'headings'
		self.treeFleet['columns'] = ('0', '1')
		self.treeFleet.column('0', width=100, anchor='c')
		self.treeFleet.column('1', width=100, anchor='c')
		self.treeFleet.heading('0', text='Vehicle Id')
		self.treeFleet.heading('1', text='Type')

		# label frame for the travel Times:
		self.lfTravelTimes = tk.ttk.LabelFrame(self.pw, text='Travel Times', padding = 5)
		self.container2 = tk.Frame(self.lfTravelTimes)
		self.treeTravelTimes = ttk.Treeview(self.container2, selectmode='browse')
		self.treeNodeId = ttk.Treeview(self.container2, selectmode='browse')
		self.scrollTTy = ttk.Scrollbar(self.container2, orient='vertical', command=self.scrollTTY)
		self.scrollTTx = ttk.Scrollbar(self.lfTravelTimes, orient='horizontal', command=self.treeTravelTimes.xview)
		self.treeTravelTimes.config(yscrollcommand=self.scrollwheelTT, xscrollcommand=self.scrollTTx)
		self.treeNodeId.config(yscrollcommand=self.scrollwheelTT)
		self.treeTravelTimes.bind('<Button-1>', self.on_treeTravelTimesClick)
		self.treeNodeId.bind('<Button-1>', self.on_treeNodeIdClick)


		self.timeSlotFrame = tk.Frame(self.lfTravelTimes)
		self.timeSlotFrame.pack(side='top', anchor='w')
		self.TWLabel = tk.Label(self.timeSlotFrame, text = 'time slot ', bg = 'grey70')
		self.TWLabel.pack( side = 'left')
		self.spinboxTimeSlot = tk.Spinbox(self.timeSlotFrame, command=self.selectTimeSlot)
		self.treeTravelTimes['show'] = 'headings'
		self.treeNodeId['show'] = 'headings'

		self.treeNodeId['columns'] = ('0')
		self.treeNodeId.column('0', width=40)
		self.treeNodeId.heading('0', text= 'Start\End')

		self.pw.add(self.lfTravelTimes, weight = 1)
		self.container2.pack(side='top', fill='both', expand=True)
		self.scrollTTy.pack(side='left', fill='y')
		self.treeNodeId.pack(side='left', fill='y',)
		self.treeTravelTimes.pack(side='left', fill='both', expand=True)
		self.scrollTTx.pack(side='top', fill='x')

	def on_addVehicleButton(self):
		vehTypeComboBox = None
		numberEF = None
		def commandHandler(result):
			if result == 'OK':
				self.guiInput.sendCommand('addVehicles '+str(numberEF.get())+ ' ' + str(vehTypeComboBox.get()))
				self.dialogAddVehicles.deactivate(result)
			else:
				self.dialogAddVehicles.deactivate(result)

		self.dialogAddVehicles = Pmw.Dialog(self, buttons = ('OK', 'Cancel'), defaultbutton = 'OK', title = 'Add Vehicle(s) to fleet', command = commandHandler)
		vehTypeList = tuple([i['VehicleType'] for i in self.carrierObj['VehicleTypes']])
		vehTypeComboBox = Pmw.ComboBox(self.dialogAddVehicles.interior(), label_text = 'Vehicle Type', labelpos = 'nw', scrolledlist_items = vehTypeList)
		vehTypeComboBox.selectitem(0, setentry=True)
		vehTypeComboBox.pack(side='top')

		numberEF = Pmw.Counter(self.dialogAddVehicles.interior(), orient = 'horizontal', entry_width = 2, entryfield_value= 1, entryfield_validate = {'validator': 'integer', 'min' :1, 'max' : 99})
		numberEF.pack(side ='top')

		self.dialogAddVehicles.withdraw()
		self.dialogAddVehicles.activate(geometry = 'centerscreenalways')

	def on_deleteFleetButton(self):
		self.guiInput.sendCommand('deleteVehicles')

	def on_loadCarrierButton(self):
		self.carrierFilename = tk.filedialog.askopenfilename(initialdir = self.lastPathUsed,title = "Select carrier file",filetypes = (("json files","*.json"),("all files","*.*")))
		if self.carrierFilename != () and self.carrierFilename != '':
			self.guiInput.sendCommand('loadCarrier '+self.carrierFilename)
			self.mainroot.setLastPathUsed(os.path.dirname(self.carrierFilename))

	def on_treeTravelTimesClick(self, event):
		'''synchronize the selections on the two treeviews of the travel times '''
		item = self.treeTravelTimes.identify('item', event.x, event.y)
		if item != '':
			itemId = self.treeNodeId.identify_row(event.y)
			self.treeNodeId.selection_set(itemId)

	def on_treeNodeIdClick(self, event):
		'''synchronize the selections on the two treeviews of the travel times '''
		item = self.treeNodeId.identify('item', event.x, event.y)
		if item != '':
			itemId = self.treeTravelTimes.identify_row(event.y)
			self.treeTravelTimes.selection_set(itemId)

		
	def extractFileName(self, filename):
		return filename.split('/')[-1]

	def displayData(self, carrierObj):
		self.carrierObj = carrierObj

		

		self.loadCarrierButton.pack_configure(side = 'bottom')

		self.efFileName.setentry(self.extractFileName(self.carrierFilename))
		self.efTimeSlotNumber.setentry(carrierObj['TimeSlotsNumber'])
		self.efTravelTimeUnit.setentry(carrierObj['Unit'])

		self.pw.pack(side = 'top', fill='both', expand = True)

		# configure the vehile types frame
		self.treeVehicleType.delete(*self.treeVehicleType.get_children())
		for vt in self.carrierObj['VehicleTypes']:
			self.treeVehicleType.insert('', 'end', values=[vt['VehicleType'], str(vt['Capacity'])])
		self.treeVehicleType.pack(side='left', anchor='nw', fill = 'both', expand = True)
		self.scrollbarVehicleType.pack(side='left', anchor = 'nw', fill='y')


		# labelFrame for the vehicle fleet
		
		self.treeFleet.delete(*self.treeFleet.get_children())
		for v in self.carrierObj['Vehicles']:
			if int(v) < len(self.colors):
				self.carrierObj['Vehicles'][v]['color'] = self.colors[int(v)]
			else:
				self.carrierObj['Vehicles'][v]['color'] = '#%06x' % random.randint(0, 0xFFFFFF)
			self.treeFleet.insert('', 'end', values=[v, self.carrierObj['Vehicles'][v]['VehicleType']])
			self.guiInput.sendCommand('setVehicleColor {} {}'.format(v, self.carrierObj['Vehicles'][v]['color']))

		self.frameButtonsFleet.pack(side='top', anchor = 'nw', fill = 'x', expand = True)
		self.addVehicleButton.pack(side = 'left', anchor = 'nw')
		self.deleteFleetButton.pack(side = 'left', anchor = 'nw')

		self.frameTreeFleet.pack(side='top', anchor = 'nw', fill = 'x', expand = True)
		self.treeFleet.pack(side='left', anchor='nw', fill = 'both', expand = True)
		self.scrollbarFleet.pack(side='left', anchor = 'nw', fill='y')


		# label frame for the travel Times:
		self.spinboxTimeSlot.config(from_= 1, to= self.carrierObj['TimeSlotsNumber'], width = 8)
		self.spinboxTimeSlot.pack(side = 'left')


		columnHeading = list(range(len(self.carrierObj['TravelTimes'][0]['VehTravelTimes'])))
		self.treeTravelTimes['columns'] = tuple([str(i) for i in columnHeading])

		self.treeTravelTimes.delete(*self.treeTravelTimes.get_children())
		self.treeNodeId.delete(*self.treeNodeId.get_children())
		for i in columnHeading:
			self.treeTravelTimes.column(str(i), width=20, minwidth=30, stretch=True, anchor='c')
			self.treeTravelTimes.heading(str(i), text=str(i))
			self.treeNodeId.insert('', 'end', values=str(i))

		

		self.selectTimeSlot()
		self.graphTab.mapCoordinateCheck()

		self.dataLoaded = True

	def getFictiveDistanceMatrix(self):
		''' return a distance matrix (not real) or None if not yet available'''
		if self.carrierObj != None and 'TravelTimes' in self.carrierObj:
			matrix = copy.deepcopy(self.carrierObj['TravelTimes'][0]['VehTravelTimes'])
			for i, val in enumerate(matrix):
				for j in range(i+1, len(val)):
					matrix[i][j] = matrix[j][i]

			return matrix

		else:
			return None


	def getColorOfVehicle(self, vehicleID):
		''' return the color associated with the vehicle with the id given, None if the id doesn't exist '''
		if str(vehicleID) in self.carrierObj['Vehicles']:
			return self.carrierObj['Vehicles'][str(vehicleID)]['color']
		else:
			return None

	def getVehicleIds(self):
		''' return a list containing the ids of the vehicle in the fleet '''
		return [vehId for vehId in self.carrierObj['Vehicles']]



	def isDataLoaded(self):
		return self.dataLoaded


			
	def selectTimeSlot(self):
		ts = int(self.spinboxTimeSlot.get())
		for el in self.carrierObj['TravelTimes']:
			if ts in el['TimeSlot']:
				self.carrierMatrix = el['VehTravelTimes']
		self.treeTravelTimes.delete(*self.treeTravelTimes.get_children())

		for line in self.carrierMatrix:
			val = [str(i) for i in line]
			self.treeTravelTimes.insert('', 'end', values=val)


			
	def scrollTTY(self, *args):
		self.treeTravelTimes.yview(*args)
		self.treeNodeId.yview(*args)

	def scrollwheelTT(self, *args):
		self.scrollTTy.set(*args)
		self.scrollTTY('moveto', args[0])

	def setGraphTab(self, graphTab):
		self.graphTab = graphTab

	def setLastPathUsed(self, path):
		self.lastPathUsed = path

	def setMapFrame(self, mapFrame):
		self.mapFrame = mapFrame

	def setSimulationFrame(self, simulationFrame):
		self.simulationFrame = simulationFrame

	def updateStatus(self, newStatus):
		self.simulationStatus = newStatus
		if self.simulationStatus in ['PreSimulation']:
			self.loadCarrierButton.config(state = 'normal')
			self.addVehicleButton.config(state = 'normal')
			self.deleteFleetButton.config(state = 'normal')

		elif self.simulationStatus in ['OfflineComputation']:
			self.loadCarrierButton.config(state = 'disabled')
			self.addVehicleButton.config(state = 'disabled')
			self.deleteFleetButton.config(state = 'disabled')

		elif self.simulationStatus in ['OfflinePauseAsked']:
			self.loadCarrierButton.config(state = 'disabled')
			self.addVehicleButton.config(state = 'disabled')
			self.deleteFleetButton.config(state = 'disabled')

		elif self.simulationStatus in ['OfflinePause']:
			self.loadCarrierButton.config(state = 'disabled')
			self.addVehicleButton.config(state = 'disabled')
			self.deleteFleetButton.config(state = 'disabled')

		elif self.simulationStatus in ['OfflineEnd']:
			self.loadCarrierButton.config(state = 'disabled')
			self.addVehicleButton.config(state = 'disabled')
			self.deleteFleetButton.config(state = 'disabled')

		elif self.simulationStatus in ['OnlineComputation']:
			self.loadCarrierButton.config(state = 'disabled')
			self.addVehicleButton.config(state = 'disabled')
			self.deleteFleetButton.config(state = 'disabled')

		elif self.simulationStatus in ['OnlinePauseAsked']:
			self.loadCarrierButton.config(state = 'disabled')
			self.addVehicleButton.config(state = 'disabled')
			self.deleteFleetButton.config(state = 'disabled')

		elif self.simulationStatus in ['OnlinePause']:
			self.loadCarrierButton.config(state = 'disabled')
			self.addVehicleButton.config(state = 'disabled')
			self.deleteFleetButton.config(state = 'disabled')

		elif self.simulationStatus in ['PostSimulation']:
			self.loadCarrierButton.config(state = 'disabled')
			self.addVehicleButton.config(state = 'disabled')
			self.deleteFleetButton.config(state = 'disabled')




