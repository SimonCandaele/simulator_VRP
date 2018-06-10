#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 15:15:57 2017

@author: simon
"""

import json

inputfile = open('/media/simon/7C9095DB90959BE8/Users/scandaele/Documents/UCL/MASTER/tfe/instance_vrp/realdata_optimod_lyon/travel_times.txt', 'r+')
outputfile = open('/media/simon/7C9095DB90959BE8/Users/scandaele/Documents/UCL/MASTER/tfe/instance_vrp/realdata_optimod_lyon/Carrier.json', 'w+')

Carrier = {}

Carrier['FileType'] = 'Carrier'
Carrier['TimeSlotsNumber'] = 96
Carrier['VehicleTypes'] = [{'VehicleType' : 'car', 'Capacity' : 200}]
Carrier['Vehicles'] = {}
# travel times unit
Carrier['Unit'] = 'Second'
for i in range(20):
    Carrier['Vehicles'][str(i)] = {'VehicleType' : 'car'}

line = inputfile.readline()
line = inputfile.readline()

travel_times = []
for i in range(255):
    line = inputfile.readline()
    # travel times in minutes
    # travel_times += [[int(round(int(i)/60)) for i in (line.split())[2:]]]
    # travel times in seconds
    travel_times += [[int(i) for i in (line.split())[2:]]]
  
Carrier['TravelTimes'] = [{'TimeSlot' : list(range(1, 96 + 1)), 'Vehicle' : 'car', 'VehTravelTimes' : travel_times}]

outputfile.write(json.dumps(Carrier, sort_keys = True, indent = 4))

inputfile.close()
outputfile.close()
