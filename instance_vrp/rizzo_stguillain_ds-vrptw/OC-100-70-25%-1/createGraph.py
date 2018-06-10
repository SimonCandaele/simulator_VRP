#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

locationFile = open('/home/simon/Documents/tfe_simon_candaele/instance_vrp/rizzo_stguillain_ds-vrptw/OC-100-70-25%-1/locations.txt', 'r')
graphfile = open('/home/simon/Documents/tfe_simon_candaele/instance_vrp/rizzo_stguillain_ds-vrptw/OC-100-70-25%-1/Graph.json', 'w+')
graphNodesId = open('/home/simon/Documents/tfe_simon_candaele/instance_vrp/rizzo_stguillain_ds-vrptw/OC-100-70-25%-1/graphNodesId.json', 'w+')

graphObj = {'FileType': 'Graph', 'Nodes': {}}
graphIdObj = {} # key : oldId, value : new id

line = ''
while line.split() != ['NODE', 'TYPE', '(LAT,LNG)', '(Y,X)']:
	line = locationFile.readline()



for line in locationFile:
	lsplit   = line.split()

	node     = lsplit[0]
	ntype    = lsplit[1]
	gpsCoord = lsplit[2]
	mapCoord = lsplit[3]

	if node not in graphIdObj:
		graphIdObj[node] = len(graphIdObj)

	node = graphIdObj[node]

	gpsCoord = gpsCoord.replace('(','')
	gpsCoord = gpsCoord.replace(')','')
	gpsCoord = gpsCoord.split(',')
	lat = float(gpsCoord[0])
	lng = float(gpsCoord[1])

	mapCoord = mapCoord.replace('(','')
	mapCoord = mapCoord.replace(')','')
	mapCoord = mapCoord.split(',')
	x = (float(mapCoord[1]))*100
	y = (1-float(mapCoord[0]))*100

	if ntype == 'DPT':
		ntype = 'Depot'
	elif ntype == 'CST' or ntype == 'LCK':
		ntype = 'Customer'


	newNode = {'NodeType':[ntype]}
	newNode['GpsCoord'] = {'lat': lat, 'lng' : lng}
	newNode['MapCoord'] = {'X' : x, 'Y': y}

	graphObj['Nodes'][node] = newNode


graphfile.write(json.dumps(graphObj,   sort_keys = True, indent = 4))
graphNodesId.write(json.dumps(graphIdObj, sort_keys = True, indent = 4))

graphfile.close()
graphNodesId.close()


