# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 11:02:35 2017

@author: scandaele
"""
import pprint
import json

class Graph:
	def __init__(self):
		self.data = {}
		self.fileLoaded = False

	def loadFile(self, GraphFile):
		"""
		Take the name of the Graph file in entry, return the Graph as a dict structure
		return True if file was loaded without problems
		return False otherwise
		"""
		try:
			with open(GraphFile) as data:
				dataLoaded = json.load(data)
				if 'FileType' not in dataLoaded:
					print('   ERROR: the field "FileType" was not found in the json file')
					print('          data can not be loaded')
					return False
				elif dataLoaded['FileType'] != 'Graph':
					print('   ERROR: the field "FileType" of the file is ', dataLoaded['FileType'])
					print('          the value of the field was expected to be "Graph"')
					return False
				else:
					self.data = dataLoaded
					self.fileLoaded = True
					return True
		except IOError:
			print('cannot open', GraphFile)
			return False

	def containsNode(self, nodeID):
		''' return True if a node with nodeID is in the data, false otherwise '''
		if 'Nodes' in self.data:
			if str(nodeID) in self.data['Nodes']:
				return True
			else:
				return False
		else:
			return False
			
	def display(self):
		pp = pprint.PrettyPrinter(indent = 4)
		pp.pprint(self.data)

	def getNodeType(self, nodeID):
		''' return a tuples with the type of the node with id "nodeID", None if such node doesn't exist '''
		if 'Nodes' in self.data:
			if str(nodeID) in self.data['Nodes']:
				return tuple(self.data['Nodes'][str(nodeID)]['NodeType'])
			else:
				return None
		else:
			return None

	def isLoaded(self):
		''' return true if a Graph file was correctly loaded'''
		return self.fileLoaded