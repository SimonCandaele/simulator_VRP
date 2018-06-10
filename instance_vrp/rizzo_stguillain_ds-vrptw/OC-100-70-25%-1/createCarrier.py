#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

fstime = open('/home/simon/Documents/tfe_simon_candaele/instance_vrp/rizzo_stguillain_ds-vrptw/OC-100-70-25%-1/service-times.txt', 'r')
fttime = open('/home/simon/Documents/tfe_simon_candaele/instance_vrp/rizzo_stguillain_ds-vrptw/OC-100-70-25%-1/travel-times.txt', 'r')

fgraph = open('/home/simon/Documents/tfe_simon_candaele/instance_vrp/rizzo_stguillain_ds-vrptw/OC-100-70-25%-1/graphNodesId.json', 'r')
graphNodesId = json.loads(fgraph.read())

fcarrier = open('/home/simon/Documents/tfe_simon_candaele/instance_vrp/rizzo_stguillain_ds-vrptw/OC-100-70-25%-1/carrier.json', 'w+')

Carrier = {}

Carrier['FileType'] = 'Carrier'
Carrier['TimeSlotsNumber'] = 5
Carrier['VehicleTypes'] = [{'VehicleType' : 'van', 'Capacity' : 700}, {'VehicleType' : 'bike', 'Capacity' : 70}]
Carrier['Vehicles'] = {}
Carrier['Unit'] = 'Second'
Carrier['TravelTimes'] = [{'TimeSlot' : [1,2,3,4], 'VehTravelTimes' : [], 'Vehicle' : 'van'}, {'TimeSlot' : [1,2,3,4], 'VehTravelTimes' : [], 'Vehicle' : 'bike'}]

line = ''
while 'NA' not in line and 'NB' not in line and 'VAN(s)' not in line and 'BIKE(s)' not in line:
	line = fttime.readline()


maxId = len(graphNodesId)
for i in range(maxId):
	Carrier['TravelTimes'][0]['VehTravelTimes'] += [[0]*maxId]
	Carrier['TravelTimes'][1]['VehTravelTimes'] += [[0]*maxId]

for line in fttime:
	lsplit = line.split()

	na = graphNodesId[lsplit[0]]
	nb = graphNodesId[lsplit[1]]
	vt = int(lsplit[2])
	bt = int(lsplit[3])

	Carrier['TravelTimes'][0]['VehTravelTimes'][na][nb] = vt
	Carrier['TravelTimes'][1]['VehTravelTimes'][na][nb] = bt

fcarrier.write(json.dumps(Carrier, sort_keys = True, indent = 4))

fstime.close()
fttime.close()
fgraph.close()
fcarrier.close()