# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 11:42:22 2017

@author: scandaele
"""
import pprint
import json
import math

class Carrier:
	def __init__(self):
		self.data = {}
		self.fileLoaded = False

	def loadFile(self, CarrierFile):
		"""
		Take the name of the Carrier file in entry, return the Carriers as a dict structure
		return True if file was loaded without problems
		return False otherwise
		"""
		try:
			with open(CarrierFile) as data:
				dataLoaded = json.load(data)
				if 'FileType' not in dataLoaded:
					print('   ERROR: the field "FileType" was not found in the json file')
					print('          data can not be loaded')
					return False
				elif dataLoaded['FileType'] != 'Carrier':
					print('   ERROR: the field "FileType" of the file is ', dataLoaded['FileType'])
					print('          the value of the field was expected to be "Carrier"')
					return False
				else:
					self.data = dataLoaded
					return True
					self.fileLoaded = True
		except IOError:
			print('cannot open', CarrierFile)
			return False
		
	def containVehicleType(self, vehType):
		"""
		return True if vehType is the name of a vehicle type in the carrier object
		return False otherwise
		"""
		if not self.data:
			return False
		for vehicleType in self.data['VehicleTypes']:
			if vehicleType['VehicleType'] == vehType:
				return True
		return False

	def display(self):
		pp = pprint.PrettyPrinter(indent = 4)
		pp.pprint(self.data)

	def getCapacityOfVehicle(self, vehicleId):
		'''
		vehicleId : the id of a vehicle in the fleet

		return the capacity of the vehicle
		'''
		vehicleType = self.data['Vehicles'][vehicleId]
		for vType in self.data['VehicleTypes']:
			if vType['VehicleType'] == vehicleType['VehicleType']:
				return vType['Capacity']
		print('ERROR: vehicle {} does not match any vehicle Type'.format(vehicleId))

	def getLatestDepartureTU(self, startNode, endNode, arrivalTime, vehicleType, myCustomer):
		"""
		return the latest possible time unit to travel from startNode to endNode,
		arriving at arrivalTime
		return False if the delay is too short between these two nodes.
		"""
		latestdepartureTU = False
		searchFinished = False
		departureTU = 0
		while not searchFinished:
			travelTime = self.getTravelTime(startNode, endNode, vehicleType, myCustomer.getTimeSlotOfTimeUnit(departureTU))
			if departureTU + travelTime > arrivalTime:
				searchFinished = True
			else:
				latestdepartureTU = departureTU
				departureTU = math.floor(departureTU+1)
		return latestdepartureTU

	def getTravelTime(self, startNode, endNode, vehicleType, timeSlotStart):
		"""
		return the travel time from startNode to endNode when starting at timeSlotStart
		"""
		if timeSlotStart == 0:
			timeSlotStart = 1
		for TT in self.data['TravelTimes']:
			if TT['Vehicle'] == vehicleType:
				if timeSlotStart in TT['TimeSlot']:
					return TT['VehTravelTimes'][startNode][endNode]

	def getVehicleType(self, vehicleId):
		"""
		return the type of the vehicle with Id vehicleId
		return False if no vehicle with this id
		"""
		if vehicleId in self.data['Vehicles']:
			return self.data['Vehicles'][vehicleId]['VehicleType']
		else:
			return False

	def getVehicleOfId(self, vehicleId):
		"""
		return true if a vehicle with such id exists
		return False otherwise
		"""
		if vehicleId in self.data['Vehicles']:
			return True
		else:
			return False

	def isLoaded(self):
		''' return true if a carrier file was correctly loaded'''
		return self.fileLoaded

	def setVehicleColor(self, vehId, color):
		''' add the color to the vehicle with id vehId in the carrier structure'''
		vehId = str(vehId)
		if 'Vehicles' in self.data:
			if vehId in self.data['Vehicles']:
				self.data['Vehicles'][vehId]['color'] = color