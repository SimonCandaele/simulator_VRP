"""
Created on Tue Oct 31 08:11:18 2017

@author: scandaele

"""
import pprint
import json
import random
import copy
from CustomerClass import Customer

class Scenario:
    def __init__(self):
        self.data = {}
        self.fileLoaded = False

    def loadFile(self, ScenarioFile):
        """
        Take the name of the Graph file in entry, return the Graph as a dict structure
        return True if file was loaded without problems
        return False otherwise
        """
        try:
            with open(ScenarioFile) as data:
                dataLoaded = json.load(data)
                if 'FileType' not in dataLoaded:
                    print('   ERROR: the field "FileType" was not found in the json file')
                    print('          data can not be loaded')
                    return False
                elif dataLoaded['FileType'] != 'Scenario':
                    print('   ERROR: the field "FileType" of the file is ', dataLoaded['FileType'])
                    print('          the value of the field was expected to be "Scenario"')
                    return False
                else:
                    self.data = dataLoaded
                    self.fileLoaded = True
                    return True
        except IOError:
            print('cannot open', ScenarioFile)
            return False

    def containsRequest(self, request):
        """
            return True if the scenario contains the request
            or a string error message describing how this request is not in the scenario
        """
        for req in self.data['Requests']:
            if req['RequestId'] == request['RequestId']:
                for field in req:
                    if field not in request:
                        return 'ERROR : request with same Id in scenario but different attributes'

                    elif field == 'TimeWindow':
                        if req['TimeWindow']['start'] != request['TimeWindow']['start'] or req['TimeWindow']['end'] != request['TimeWindow']['end']:
                            return 'ERROR : request with same Id in scenario but different TimeWindow'

                    elif req[field] != request[field]:
                        return 'ERROR : request with same Id in scenario but different attributes'

                return True
        return 'ERROR : no such RequestId in scenario'
        
    def display(self):
        pp = pprint.PrettyPrinter(indent = 4)
        pp.pprint(self.data)
    
    def generateScenario(self, myCustomer, ComputationTime = 5.0, OfflineTime = 0.0):
        """ 
            Take a customers structure in entry, generate a scenario and saved it in self.data
        """
        Requests = []
        self.data = {'ComputationTime' : ComputationTime, 'OfflineTime' : OfflineTime, 'Requests' : Requests}
        self.data['FileType'] = 'Scenario'

        #Iterate on each potential request to maybe generate it.
        for req in myCustomer.data['PotentialRequests']:
            PotentialRequest = copy.deepcopy(req)
            PotentialRequest['Type'] = 'InitialRequest'
            RandomNum = random.randint(1,100)
            ProbSum = 0
            TsIndex = 0
            Probabilities = iter(PotentialRequest['ArrivalProbability'])
            while TsIndex < myCustomer.data['TimeSlotsNumber'] and ProbSum < RandomNum:
                ProbSum += next(Probabilities)
                if ProbSum > RandomNum:
                    if PotentialRequest['TimeWindow']['TWType'] == 'absolute' :  
                        timeUnit = random.randint(myCustomer.data['TimeSlots'][TsIndex], myCustomer.data['TimeSlots'][TsIndex + 1] - 1)
                        if TsIndex == 0:
                            self.addRequest(PotentialRequest, timeUnit, TsIndex-1)
                        else:
                            self.addRequest(PotentialRequest, timeUnit, TsIndex)
                    elif PotentialRequest['TimeWindow']['TWType'] == 'relative' :
                        timeUnit = random.randint(myCustomer.data['TimeSlots'][TsIndex], myCustomer.data['TimeSlots'][TsIndex + 1] - 1)
                        if TsIndex == 0:
                            self.addRequest(PotentialRequest, timeUnit, TsIndex-1)
                        else:
                            self.addRequest(PotentialRequest, timeUnit, TsIndex)
                TsIndex += 1
        self.data['Requests'] = sorted(self.data['Requests'], key=lambda k: k['RevealTime'])
        self.fileLoaded = True

    def getRequest(self, reqId):
        """
            Return the request in the scenario corresponding to ReqId
            If no such request exists, return False
        """
        for request in self.data["Requests"]:
            if int(request["RequestId"]) == int(reqId):
                val =  copy.deepcopy(request)
                return val

        print('THE UNEXISTING REQUEST ID IS : ' + str(reqId))
        return False

    def isLoaded(self):
        ''' return true if a scenario file was correctly loaded'''
        return self.fileLoaded
            
    def addRequest(self, PotentialRequest, timeUnit, timeSlot):
        """Take a Scenario structure, a potential request structure and a timeslot index
        Add the request corresponding to the potential request to the scenario structure"""    

        NewRequest = copy.deepcopy(PotentialRequest)
        del NewRequest['ArrivalProbability']
        NewRequest['RevealTime'] = timeUnit
        NewRequest['TimeSlot'] = timeSlot
        if 'TimeWindow' in NewRequest.keys():
            if NewRequest['TimeWindow']['TWType'] == 'relative':
                NewRequest['TimeWindow'] = {'start' : timeUnit, 'end' : timeUnit + NewRequest['TimeWindow']['TimeWindowDuration']}
                del NewRequest['TimeWindow']['TimeWindowDuration']
            del(NewRequest['TimeWindow']['TWType'])

        self.data['Requests'] += [NewRequest]

    def addNewRequest(self, newRequest):
        IdMin = -1
        for req in self.data['Requests']:
            if req['RequestId'] <= IdMin:
                IdMin = req['RequestId'] - 1
        newRequest['RequestId'] = IdMin
        self.data['Requests'] += [newRequest]


    def markInitialRequest(self, customerData):
        ''' mark the requests in the scenario as initialRequest if the request is in the customerData
            mark the other as Manual '''
        customerData = copy.deepcopy(customerData)

        for requestS in self.data['Requests']:
            requestS['Type'] = None
            for requestC in customerData['PotentialRequests']:
                if requestC['RequestId'] == requestS['RequestId']:
                    requestS['Type'] = 'InitialRequest'
                    customerData['PotentialRequests'].remove(requestC)
                    break
            if requestS['Type'] == None:
                requestS['Type'] = 'Manual'







    


 
    
    
    
    
    
    
    
    
    
    