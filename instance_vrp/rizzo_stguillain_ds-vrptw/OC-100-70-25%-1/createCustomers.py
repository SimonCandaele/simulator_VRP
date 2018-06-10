#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import copy

fbehavior = open('/home/simon/Documents/tfe_simon_candaele/instance_vrp/rizzo_stguillain_ds-vrptw/OC-100-70-25%-1/5-7-0-0/lockers-no/behaviors.txt', 'r')
fstime = open('/home/simon/Documents/tfe_simon_candaele/instance_vrp/rizzo_stguillain_ds-vrptw/OC-100-70-25%-1/service-times.txt', 'r')

fgraph = open('/home/simon/Documents/tfe_simon_candaele/instance_vrp/rizzo_stguillain_ds-vrptw/OC-100-70-25%-1/graphNodesId.json', 'r')
graphNodesId = json.loads(fgraph.read())

fcustomer = open('/home/simon/Documents/tfe_simon_candaele/instance_vrp/rizzo_stguillain_ds-vrptw/OC-100-70-25%-1/Customer.json', 'w+')



def createCustomerFile(fbehavior, fstime, graphNodesId, fcustomer):
	# first read the service time
	STime = {}

	line = ''
	fstime.seek(0)
	while 'NODE' not in line or 'TYPE' not in line or 'VAN(s)' not in line:
		line = fstime.readline()

	line = fstime.readline()

	for line in fstime:
		lsplit = line.split()
		node = graphNodesId[lsplit[0]]

		STime[node] = {'van': int(lsplit[2]) , 'bike': int(lsplit[3])}






	Customer = {}
	Customer['FileType']                = 'Customers'
	Customer['TimeSlotsNumber']         = 5
	Customer['RealDurationPerTimeUnit'] = 60
	Customer['RealTimeUnit']            = 'Second'
	Customer['TimeSlots']               = [-1, 0, 120, 240, 360]
	Customer['HorizonSize']             = 480
	Customer['PotentialRequests']       = []


	line = ''
	while 'NODE' not in line or 'TYPE' not in line or 'VOL' not in line:
		line = fbehavior.readline()

	line = fbehavior.readline()

	reqCount = 0
	for line in fbehavior:
		lsplit = line.split()


		newRequest = {}

		newRequest['Demand']             = int(lsplit[2])
		newRequest['Node']               = graphNodesId[lsplit[0]]
		
		newRequest['ServiceDuration']    = int(STime[newRequest['Node']]['van']/60)
		newRequest['TimeWindow']         = {'TWType': 'absolute'}

		tw = lsplit[-6].replace('[', '')
		tw = tw.replace(']', '')
		tw = tw.split('-')
		start = tw[0].split(':')
		end   = tw[1].split(':')

		start = (int(start[0])-9)*60 + int(start[1])
		end = (int(end[0])-9)*60 + int(end[1]) +1

		newRequest['TimeWindow']         = {'TWType': 'absolute', 'start' : start, 'end' : end}


		Probs = [int(float(i)*100) for i in lsplit[-5:]]
		for i, p in enumerate(Probs):
			if p > 0 :
				prob = [0]*len(Probs)
				prob[i] = p

				newRequest['ArrivalProbability'] = prob
				reqCount += 1
				newRequest['RequestId']          = reqCount
				Customer['PotentialRequests'] += [copy.deepcopy(newRequest)]



	fcustomer.write(json.dumps(Customer, sort_keys = True, indent = 4))


FBehavior = []
FCustomer = []
FBehavior += [open('/home/simon/Documents/tfe_simon_candaele/instance_vrp/rizzo_stguillain_ds-vrptw/OC-100-70-25%-1/5-7-0-0/lockers-no/behaviors.txt', 'r')]
FBehavior += [open('/home/simon/Documents/tfe_simon_candaele/instance_vrp/rizzo_stguillain_ds-vrptw/OC-100-70-25%-1/12-18-0-0/lockers-no/behaviors.txt', 'r')]
FBehavior += [open('/home/simon/Documents/tfe_simon_candaele/instance_vrp/rizzo_stguillain_ds-vrptw/OC-100-70-25%-1/23-34-0-0/lockers-no/behaviors.txt', 'r')]

FCustomer += [open('/home/simon/Documents/tfe_simon_candaele/instance_vrp/rizzo_stguillain_ds-vrptw/OC-100-70-25%-1/5-7-0-0/lockers-no/Customer.json', 'w+')]
FCustomer += [open('/home/simon/Documents/tfe_simon_candaele/instance_vrp/rizzo_stguillain_ds-vrptw/OC-100-70-25%-1/12-18-0-0/lockers-no/Customer.json', 'w+')]
FCustomer += [open('/home/simon/Documents/tfe_simon_candaele/instance_vrp/rizzo_stguillain_ds-vrptw/OC-100-70-25%-1/23-34-0-0/lockers-no/Customer.json', 'w+')]



fstime = open('/home/simon/Documents/tfe_simon_candaele/instance_vrp/rizzo_stguillain_ds-vrptw/OC-100-70-25%-1/service-times.txt', 'r')

fgraph = open('/home/simon/Documents/tfe_simon_candaele/instance_vrp/rizzo_stguillain_ds-vrptw/OC-100-70-25%-1/graphNodesId.json', 'r')
graphNodesId = json.loads(fgraph.read())


for fi, f in enumerate(FBehavior):
	createCustomerFile(f, fstime, graphNodesId, FCustomer[fi])
	f.close()
	FCustomer[fi].close()



fbehavior.close()
fstime.close()
fgraph.close()
fcustomer.close()
