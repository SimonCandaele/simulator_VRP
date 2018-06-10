# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 11:02:55 2017

@author: scandaele
"""
import pprint
import json

class Customer:
	def __init__(self):
		self.data = {}
		self.fileLoaded = False

	def display(self):
		pp = pprint.PrettyPrinter(indent = 4)
		pp.pprint(self.data)


	def getTimeSlotOfTimeUnit(self, timeUnit):
		"""
		return the number of the timeslot containing the timeUnit
		return False if no timeslot are in this timeUnit
		"""
		if timeUnit >= self.data['HorizonSize'] or timeUnit < -1:
			return False
		else:
			for ts in range(0,self.data['TimeSlotsNumber']):
				if timeUnit < self.data['TimeSlots'][ts]:
					return ts-1

	def getHorizonSize(self):
		''' return the Horizon Size, that is the number of time unit. Return None if not in Customer data'''
		if 'HorizonSize' in self.data:
			return self.data['HorizonSize']
		else:
			return None

	def isLoaded(self):
		''' return true if a customer file was correctly loaded'''
		return self.fileLoaded


	def loadFile(self, CustomerFile):
		"""
		Take the name of the Customer file in entry, return the Customer as a dict structure
		return True if file was loaded without problems
		return False otherwise
		"""
		try:
			with open(CustomerFile) as data:
				dataLoaded = json.load(data)
				if 'FileType' not in dataLoaded:
					print('   ERROR: the field "FileType" was not found in the json file')
					print('          data can not be loaded')
					return False
				elif dataLoaded['FileType'] != 'Customers':
					print('   ERROR: the field "FileType" of the file is ', dataLoaded['FileType'])
					print('          the value of the field was expected to be "Customers"')
					return False
				else:
					self.data = dataLoaded
					self.fileLoaded = True
					return True
		except IOError:
			print('cannot open', CustomerFile)
			return False
	        
	
    