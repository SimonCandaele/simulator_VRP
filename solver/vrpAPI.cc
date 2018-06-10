/*
 *
 * Copyright 2015 gRPC authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

#include "vrpAPI.h"




// Logic and data behind the server's behavior.
class SimulatorMessagesHandler final : public SimulatorMessages::Service {
public: 
  vrpApi *smhAPI;

private:
  Status isReady(ServerContext* context, const Empty* request,
                  BoolMessage* reply) override {
    (void) context;
    (void) request;
    //std::cout << "--------------->try acquire lock >0<";
    smhAPI->vrpApiMutex.lock();
    //std::cout << "tryit >0<\n";
    reply->set_b(smhAPI->isready);
    //std::cout << "----------------> unlock >0<\n";
    smhAPI->vrpApiMutex.unlock();
    
    return Status::OK;
  }

  Status isReadyForOffline(ServerContext* context, const Empty* request,
                  BoolMessage* reply) override {
    (void) context;
    (void) request;
    //std::cout << "try acquire lock >1<";
    smhAPI->vrpApiMutex.lock();
    //std::cout << "tryit >1<\n";
    reply->set_b(smhAPI->isReadyForOffline);
    //std::cout << "----------------> unlock >1<\n";
    smhAPI->vrpApiMutex.unlock();
    
    return Status::OK;
  }

  Status isReadyForOnline(ServerContext* context, const Empty* request,
                  BoolMessage* reply) override {
    (void) context;
    (void) request;
    //std::cout << "try acquire lock >2<";
    smhAPI->vrpApiMutex.lock();
    //std::cout << "tryit >2<\n";
    reply->set_b(smhAPI->isReadyForOnline);
    //std::cout << "----------------> unlock >2<\n";
    smhAPI->vrpApiMutex.unlock();
    
    return Status::OK;
  }

  Status loadJson(ServerContext* context, const JsonMessage* request,
                  Empty* reply) override {
    (void) context;
    (void) reply;
    //std::cout << "try acquire lock >3<";
    smhAPI->vrpApiMutex.lock();
    //std::cout << "tryit >3<\n";
    json jsonmsg = json::parse(request->jsonstring());
    
    for (json::iterator it = jsonmsg.begin(); it != jsonmsg.end(); it++){
      if(it.key() == "Graph"){
        smhAPI->vrpInstance["Graph"] = it.value();
        smhAPI->dataChanged = true;
      }
      else if(it.key() == "Carrier"){
        smhAPI->vrpInstance["Carrier"] = it.value();
        smhAPI->dataChanged = true;
      }
      else if(it.key() == "Customers"){
        smhAPI->vrpInstance["Customers"] = it.value();
        smhAPI->horizonSize = smhAPI->vrpInstance["Customers"]["HorizonSize"];
        smhAPI->dataChanged = true;
      }
      else if(it.key() == "NewRequests"){
        json newRequest;
        newRequest = jsonmsg["NewRequests"];
        smhAPI->vrpInstance["Scenario"]["Requests"] += newRequest;
        smhAPI->newRequestQueue.push(newRequest);
        //std::cout << "vrapAPI.cc :: new request arrived at : " << smhAPI->getCurrentTimeUnit() << " \n";
        smhAPI->dataChanged = true;
      }
      else {
        smhAPI->vrpInstance[it.key()] = it.value();
        smhAPI->dataChanged = true;
      }
      if(smhAPI->verbose){
        std::cout << "loadJson " << it.key() << std::endl;
      }
    }
     //std::cout << "----------------> unlock >3<\n";
    smhAPI->vrpApiMutex.unlock();
   
    return Status::OK;
  }

  Status currentTimeUnit(ServerContext* context, const TimeUnitMessage* request,
                  Empty* reply) override {
    (void) context;
    (void) reply;
    if(not smhAPI->simulationStarted){
      smhAPI->simulationStarted = true;
    }
    //std::cout << "try acquire lock >4<";
    smhAPI->vrpApiMutex.lock();
    //std::cout << "tryit >4<\n";
    smhAPI->currentTU = request->timeunit();
    //std::cout << "----------------> unlock >4<\n";
    smhAPI->vrpApiMutex.unlock();
    
    if(smhAPI->verbose){
      std::cout << "currentTimeUnit " << smhAPI->currentTU << std::endl;
    }
    return Status::OK;
  }

  Status pauseSimulation(ServerContext* context, const Empty* request,
                  DoubleMessage* reply) override {
    (void) context;
    (void) request;
    //std::cout << "try acquire lock >5<";
    smhAPI->vrpApiMutex.lock();
    //std::cout << "tryit >5<\n";
    smhAPI->askPause = true;
    //std::cout << "----------------> unlock >5<\n";
    smhAPI->vrpApiMutex.unlock();
    



    auto f = smhAPI->beginPause.get_future();
    f.wait();
    double replyValue = f.get();
    reply->set_value(replyValue);

    smhAPI->beginPause = std::promise<double>{}; 
    
    if(smhAPI->verbose){
      std::cout << "pauseSimulation" << std::endl;
    }
    return Status::OK;
  }

  Status continueSimulation(ServerContext* context, const Empty* request,
                  DoubleMessage* reply) override {
    (void) context;
    (void) request;
    //std::cout << "try acquire lock >6<";
    smhAPI->vrpApiMutex.lock();
    //std::cout << "tryit >6<\n";
    smhAPI->askPause = false;
    //std::cout << "----------------> unlock >6<\n";
    smhAPI->vrpApiMutex.unlock();
    

    smhAPI->endPauseTime = std::chrono::system_clock::now() + std::chrono::seconds(5);
    double pauseDuration = std::chrono::duration_cast<std::chrono::nanoseconds>( smhAPI->endPauseTime - smhAPI->startPauseTime ).count();
    pauseDuration = pauseDuration/1000000000;

    smhAPI->totalPauseTime = smhAPI->totalPauseTime + pauseDuration;

    smhAPI->endPause.set_value();
    double endPauseTimeDouble = std::chrono::duration_cast<std::chrono::nanoseconds> (smhAPI->endPauseTime.time_since_epoch()).count();
    endPauseTimeDouble = endPauseTimeDouble/1000000000;



    reply->set_value(endPauseTimeDouble);
    if(smhAPI->verbose){
      std::cout << "continueSimulation" << std::endl;
    }
    return Status::OK;

  }

  Status setCurrentSolution(ServerContext* context, const JsonMessage* request,
                  Empty* reply) override {
    (void) context;
    (void) reply;
    //std::cout << "try acquire lock >7<";
    smhAPI->vrpApiMutex.lock();
    //std::cout << "tryit >7<\n";
    smhAPI->simulatorSolution = json::parse(request->jsonstring());
    smhAPI->newSimulatorSolution = true;
    smhAPI->vrpApi::updateBestSolution(smhAPI->simulatorSolution);
    //std::cout << "----------------> unlock >7<\n";
    smhAPI->vrpApiMutex.unlock();
    
    if(smhAPI->verbose){
      std::cout << "Receive a solution from the simulator" << std::endl;
    }
    return Status::OK;
  }

  Status shutdown(ServerContext* context, const Empty* request,
                  Empty* reply) override {
    (void) context;
    (void) request;
    (void) reply;
    //std::cout << "try acquire lock >8<";
    smhAPI->vrpApiMutex.lock();
    //std::cout << "tryit >8<\n";
    smhAPI->vrpApiexit_requested.set_value();
    smhAPI->endSimulation = true;
    smhAPI->simulationState = smhAPI->stateOfSimulation::onlineEnd;
    //std::cout << "----------------> unlock >8<\n";
    smhAPI->vrpApiMutex.unlock();
    
    if(smhAPI->verbose){
      std::cout << "shutdown" << std::endl;
    }
    return Status::OK;
  }

  Status testConnection(ServerContext* context, const Empty* request,
                  Empty* reply) override {
    (void) context;
    (void) request;
    (void) reply;
    if(smhAPI->verbose){
      std::cout << "testConnection" << std::endl;
    }
    return Status::OK;
  }

  Status startSimulation(ServerContext* context, const Empty* request,
                  DoubleMessage* reply) override {
    (void) context;
    (void) request;
    if(smhAPI->verbose){
      std::cout << "startSimulation" << std::endl;
    }

    std::chrono::time_point<std::chrono::system_clock> startTime = std::chrono::system_clock::now();
    startTime += std::chrono::seconds(4);

    double startTimeDouble = std::chrono::duration_cast<std::chrono::nanoseconds> (startTime.time_since_epoch()).count();
    startTimeDouble = startTimeDouble/1000000000;
    
    reply->set_value(startTimeDouble);


    std::unique_lock<std::recursive_mutex> lck(smhAPI->vrpApiMutex);
    smhAPI->start = startTime;
    smhAPI->simulationStarted = true;
    smhAPI->vrpApiSimulationStarted.set_value();
    return Status::OK;
  }

  Status startOfflineSimulation(ServerContext* context, const Empty* request,
                  DoubleMessage* reply) override {
    (void) context;
    (void) request;
    if(smhAPI->verbose){
      std::cout << "startOfflineSimulation" << std::endl;
    }

    std::chrono::time_point<std::chrono::system_clock> startTime = std::chrono::system_clock::now();
    startTime += std::chrono::seconds(4);

    double startTimeDouble = std::chrono::duration_cast<std::chrono::nanoseconds> (startTime.time_since_epoch()).count();
    startTimeDouble = startTimeDouble/1000000000;
    
    reply->set_value(startTimeDouble);


    std::unique_lock<std::recursive_mutex> lck(smhAPI->vrpApiMutex);
    smhAPI->startOffline = startTime;
    smhAPI->offlineSimulationStarted = true;
    smhAPI->vrpApiOfflineSimulationStarted.set_value();
    return Status::OK;
  }

  Status startOnlineSimulation(ServerContext* context, const Empty* request,
                  DoubleMessage* reply) override {
    (void) context;
    (void) request;
    if(smhAPI->verbose){
      std::cout << "vrpAPI.cc :: startOnlineSimulation" << std::endl;
    }

    std::chrono::time_point<std::chrono::system_clock> startTime = std::chrono::system_clock::now();
    startTime += std::chrono::seconds(4);

    double startTimeDouble = std::chrono::duration_cast<std::chrono::nanoseconds> (startTime.time_since_epoch()).count();
    startTimeDouble = startTimeDouble/1000000000;
    
    reply->set_value(startTimeDouble);


    std::unique_lock<std::recursive_mutex> lck(smhAPI->vrpApiMutex);
    smhAPI->startOnline = startTime;
    smhAPI->onlineSimulationStarted = true;
    smhAPI->vrpApiOnlineSimulationStarted.set_value();
    return Status::OK;
  }


};





class SolverMessagesImpl {
 public: 
  SolverMessagesImpl(std::shared_ptr<Channel> channel)
      : stub_(SolverMessages::NewStub(channel)) {}

  void acceptRequest(const std::string& requestjson){
    JsonMessage request;
    request.set_jsonstring(requestjson);
    Empty reply;
    ClientContext context;
    Status status = stub_->acceptRequest(&context, request, &reply);

    if (!status.ok()) {
      std::cout << status.error_code() << ": " << status.error_message()
                << std::endl;
    }
  }


  void notifyEndOffline(){
    Empty request;
    Empty reply;
    ClientContext context;
    Status status = stub_->notifyEndOffline(&context, request, &reply);
    if(!status.ok()) {
      std::cout << status.error_code() << ": " << status.error_message()
                << std::endl;
    }
  }

  void notifyEndOnline(){
    Empty request;
    Empty reply;
    ClientContext context;
    Status status = stub_->notifyEndOnline(&context, request, &reply);
    if(!status.ok()) {
      std::cout << status.error_code() << ": " << status.error_message()
                << std::endl;
    }
  }

  void sendBestSolution(const std::string& solutionjson) {
    JsonMessage request;
    request.set_jsonstring(solutionjson);
    Empty reply;
    ClientContext context;
    Status status = stub_->sendBestSolution(&context, request, &reply);

    if (!status.ok()) {
      std::cout << status.error_code() << ": " << status.error_message()
                << std::endl;
    }
    //else{
    //   std::cout << "  vrpAPI.cc :: sendBestSolution() used \n";
    // } 
  }

  bool testConnection() {
    Empty request;
    Empty reply;
    ClientContext context;
    Status status = stub_->testConnection(&context, request, &reply);

    if(!status.ok()) {
      return false;
    }
    return true;
  }

  double getTimeUnit() {
    Empty request;
    TimeUnitMessage reply;
    ClientContext context;
    Status status = stub_->getTimeUnit(&context, request, &reply);
    if(!status.ok()) {
      return -1.0;
    }
    return reply.timeunit();
  }

 private:
  std::unique_ptr<SolverMessages::Stub> stub_;
};




vrpApi::vrpApi(){
  verbose = false;
  currentTU = -1;
  simulatorSolution = "{}"_json;
  newSimulatorSolution = false;
  numberOfSolutions = 0;
  isready = false;
  simulationStarted = false;

  offlineSimulationStarted = false;
  onlineSimulationStarted = false;

  simulatorPort = -1;
  solverPort = -1;
  endSimulation = false;
  dataChanged = false;
  totalPauseTime = 0.0;
  vrpInstance = "{}"_json;
  simulationState = preSimulation;
}


bool vrpApi::acceptRequest(json request, bool accept){
  request["TimeOfApproval"] = getCurrentTimeUnit();
  request["Accepted"] = accept;
  json jsonMsg = "{}"_json;
  jsonMsg["messageType"] = "acceptedRequest";
  jsonMsg["request"] = request;
  // solution must be submit during offlinecomputation or onlincomputation
  if(request["TimeOfApproval"] != -2){
    //std::cout << "try acquire lock >9<";  
    vrpApiMutex.lock();
    //std::cout << "tryit >9<\n";
    if(messagesToSimulator.empty()){
      //std::cout << "acceptRequest :: before set value\n";
      messageToSend.set_value(true);
      //std::cout << "acceptRequest :: after set value\n";
    }
    messagesToSimulator.push(jsonMsg);
    //std::cout << "----------------> unlock >9<\n";
    vrpApiMutex.unlock();
    
    return true;
  }else{
    return false;
  }
}


void vrpApi::startListeningSimulator(bool verboseAPI) {
  std::ifstream infile("./../Config/config.txt");

  std::string str;
  while(std::getline(infile, str)){
    std::string solverPN("SolverPort = ");
    std::string simulatorPN("SimulatorPort = ");
    std::string::size_type sz;
    if(str.find(solverPN) == 0){
      str.erase(str.begin(), str.begin()+13);
      solverPort = std::stoi(str, &sz);
    } else if (str.find(simulatorPN) == 0){
      str.erase(str.begin(), str.begin()+16);
      simulatorPort = std::stoi(str, &sz);
    }
  }

  int rc = pthread_create(&listenerThread, NULL, RunServer, (void *) this);
  if (rc) {
    std::cout << "Error:unable to create listenerThread," << rc << std::endl;
    exit(-1);
  }
  askPause = false;
  inPause = false;
  verbose = verboseAPI;
}

std::string vrpApi::getCurrentSimulationState(){
  // update the simulation state and return the current (updated) simulation state
  double elapsedSeconds = 0.0;
  double currentTU = 0.0;
  switch(simulationState){
    case preSimulation:
      return "preSimulation";
      break;

    case offlineComputation:
      currentTime = std::chrono::system_clock::now();
      elapsedSeconds = std::chrono::duration_cast<std::chrono::nanoseconds> (currentTime-startOffline).count();
      elapsedSeconds = elapsedSeconds/1000000000;
      currentTU = -1.0 + (elapsedSeconds - totalPauseTime)/(double)vrpInstance["OfflineTime"];
      if (currentTU >= 0.0){
        //std::cout << "try acquire lock >10<";
        vrpApiMutex.lock();
        //std::cout << "tryit >10<\n";
        // update the simulation state
        simulationState = offlineEnd;


        // We do not send an endOffline message to the simulator here but in the function ready


        // notify a the runServer function to send a message 
        // if(messagesToSimulator.empty()){
        //   //std::cout << " getCurrentState::offline::before set value \n";
        //   messageToSend.set_value(true);
        //   //std::cout << " getCurrentState::offline::after set value \n";
        // }
        // json jsonMsg = "{}"_json;
        // jsonMsg["messageType"] = "endOffline";
        // messagesToSimulator.push(jsonMsg);
        // //std::cout << "----------------> unlock >10<\n";
        vrpApiMutex.unlock();
        
        return "offlineEnd";
      }else{
        return "offlineComputation";
      }
      break;

    case offlinePause:
      return "offlinePause";
      break;

    case offlineEnd:
      return "offlineEnd";
      break;

    case onlineComputation:
      currentTime = std::chrono::system_clock::now();
      elapsedSeconds = std::chrono::duration_cast<std::chrono::nanoseconds> (currentTime-startOnline).count();
      elapsedSeconds = elapsedSeconds/1000000000;
      currentTU = (elapsedSeconds - totalPauseTime)/(double)vrpInstance["ComputationTime"];
      if(currentTU > horizonSize){
        //std::cout << "try acquire lock >11<";
        vrpApiMutex.lock();
        //std::cout << "tryit >11<\n";
        // mise à jour du status
        simulationState = onlineEnd;
        if(messagesToSimulator.empty()){
          // notify the RunServer function to send a message
          //std::cout << " getCurrentState::online::before set value \n";
          messageToSend.set_value(true);
          //std::cout << " getCurrentState::online::after set value \n";
        }
        json jsonMsg = "{}"_json;
        jsonMsg["messageType"] = "endOnline";
        messagesToSimulator.push(jsonMsg);
        //std::cout << "----------------> unlock >11<\n";
        vrpApiMutex.unlock();
        
        return "onlineEnd";
      }
      return "onlineComputation";
      break;

    case onlinePause:
      return "onlinePause";
      break;

    case onlineEnd:
      return "onlineEnd";
      break;
  }
  return "nullState";
}

double vrpApi::getCurrentTimeUnit(){
  double elapsedSeconds = 0.0;
  double currentTU = 0.0;
  
  switch(simulationState){
      case preSimulation:
        std::cout << "ERROR :: function getCurrentTimeUnit called\n";
        std::cout << "         but the simulation is in state preSimulation\n";
        break;

      case offlineComputation:
        // if the current state is offlineComputation, we compute the time and update the simulation state if necessary
        currentTime = std::chrono::system_clock::now();
        elapsedSeconds = std::chrono::duration_cast<std::chrono::nanoseconds> (currentTime-startOffline).count();
        elapsedSeconds = elapsedSeconds/1000000000;
        currentTU = -1.0 + (elapsedSeconds - totalPauseTime)/(double)vrpInstance["OfflineTime"];
        updateSimulationState(currentTU);

        // this condition ensures that if the simulation was in state offlineComputation
        // when the function was called and that we reach the end of the offline time
        // we will not return the value of the currentTu, but the value -2 at the end of this function.
        if(currentTU < 0){
          return currentTU;
        }
        break;

      case offlinePause:
        std::cout << "ERROR :: function getCurrentTimeUnit called\n";
        std::cout << "         but the simulation is in state offlinePause\n";
        break;

      case offlineEnd:
        // std::cout << "ERROR :: function getCurrentTimeUnit called\n";
        // std::cout << "         but the simulation is in state offlineEnd\n";
        break;

      case onlineComputation:
        currentTime = std::chrono::system_clock::now();
        elapsedSeconds = std::chrono::duration_cast<std::chrono::nanoseconds> (currentTime-startOnline).count();
        elapsedSeconds = elapsedSeconds/1000000000;
        currentTU = (elapsedSeconds - totalPauseTime)/(double)vrpInstance["ComputationTime"];
        updateSimulationState(currentTU);
        if(currentTU < (double) horizonSize){
          return currentTU;
        }
        // }else{
        //   return (double) horizonSize;
        // }
        break;

      case onlinePause:
        std::cout << "ERROR :: function getCurrentTimeUnit called\n";
        std::cout << "         but the simulation is in state onlinePause\n";
        break;

      case onlineEnd:
        return (double) horizonSize;
        break;

      default:
        std::cout << "ERROR :: function getCurrentTimeUnit called\n";
        std::cout << "         but the simulation state could not be determined\n";
        break;
    }
  // if the simulation is neither offline or online, return a TU that do not exist
  return -2;
}

json vrpApi::getNewCurrentSolution(){
  //std::cout << "try acquire lock >12<";
  vrpApiMutex.lock();
  //std::cout << "tryit >12<\n";
  json data = simulatorSolution;
  this->newSimulatorSolution = false;
  //std::cout << "----------------> unlock >12<\n";
  vrpApiMutex.unlock();
  
  return data;
}

json vrpApi::getVrpData(){
  //std::cout << "try acquire lock >13<";
  vrpApiMutex.lock();
  //std::cout << "tryit >13<\n";
  json data = vrpInstance;
  this->dataChanged = false;
  //std::cout << "----------------> unlock >13<\n";
  vrpApiMutex.unlock();
  
  return data;
}

bool vrpApi::isNewCurrentSolution(){
  //std::cout << "try acquire lock >14<";
  vrpApiMutex.lock();
  //std::cout << "tryit >14<\n";
  bool response = newSimulatorSolution;
  //std::cout << "----------------> unlock >14<\n";
  vrpApiMutex.unlock();
  
  return response;
}

bool vrpApi::isNewRequests(){
  if(!newRequestQueue.empty()){
    json nR = "{}"_json;
    nR = newRequestQueue.front();
    if((double) nR["RevealTime"] <= getCurrentTimeUnit()){
      return true;
    }
  }
  return false;
}

void vrpApi::pauseIfSimulatorAsks(){
  bool mustSartThePause = false;
  //std::cout << "try acquire lock >15<";
  vrpApiMutex.lock();
  //std::cout << "tryit >15<\n";
  mustSartThePause = askPause;
  //std::cout << "----------------> unlock >15<\n";
  vrpApiMutex.unlock();
  

  if(mustSartThePause){
    switch(simulationState){
      case preSimulation:
        std::cout << "ERROR :: function pauseIfSimulatorAsks called\n";
        std::cout << "         but the simulation is in state preSimulation\n";
        break;

      case offlinePause:
        std::cout << "ERROR :: function pauseIfSimulatorAsks called\n";
        std::cout << "         but the simulation is in state offlinePause\n";
        break;

      case offlineEnd:
        std::cout << "ERROR :: function pauseIfSimulatorAsks called\n";
        std::cout << "         but the simulation is in state offlineEnd\n";
        break;

      case onlinePause:
        std::cout << "ERROR :: function pauseIfSimulatorAsks called\n";
        std::cout << "         but the simulation is in state onlinePause\n";
        break;

      case onlineEnd:
        std::cout << "ERROR :: function pauseIfSimulatorAsks called\n";
        std::cout << "         but the simulation is in state onlineEnd\n";
        break;

      case offlineComputation:
        simulationState = offlinePause;
        break;

      case onlineComputation:
        simulationState = onlinePause;
        break;

      default:
        std::cout << "ERROR :: function pauseIfSimulatorAsks called\n";
        std::cout << "         but the simulation state could not be determined\n";
        break;
    }

    inPause = true;
    startPauseTime = std::chrono::system_clock::now();

    double startPauseTimeDouble = std::chrono::duration_cast<std::chrono::nanoseconds> (startPauseTime.time_since_epoch()).count();
    startPauseTimeDouble = startPauseTimeDouble/1000000000;
    beginPause.set_value(startPauseTimeDouble);

    std::cout << "vrapApi:: start the pause \n";

    auto f = endPause.get_future();
    f.wait();

    std::cout << "vrapApi:: end the wait \n";


    endPause = std::promise<void>{};

    if(simulationState == offlinePause){
      simulationState = offlineComputation;
    }
    else if (simulationState == onlinePause){
      simulationState = onlineComputation;
    }else{
      std::cout << "ERROR :: the simulation should be in a pause state\n";
      std::cout << "         at the end of function pauseIfSimulatorAsks\n";
    }

    while(inPause){
      if(endPauseTime < std::chrono::system_clock::now()){
        inPause = false;
      }
    }
    //std::cout << "vrapApi:: out of while loop\n";

  }
}

json vrpApi::popNewRequest(){
  json nR = "{}"_json;
  if(!newRequestQueue.empty()){
    nR = newRequestQueue.front();
    if((double) nR["RevealTime"] <= getCurrentTimeUnit()){
      newRequestQueue.pop();
    }else{
      return "{}"_json;
    }
  }
  return nR;
}

bool vrpApi::vrpDataChanged(){
  //std::cout << "try acquire lock >16<";
  vrpApiMutex.lock();
  //std::cout << "tryit >16<\n";
  bool b = dataChanged;
  //std::cout << "----------------> unlock >16<\n";
  vrpApiMutex.unlock();
  
  return b;
}


bool vrpApi::updateBestSolution(json newSolution){

  newSolution["TimeUnitOfSubmission"] = getCurrentTimeUnit();
  if(simulationState == offlineEnd){
    newSolution["TimeOfSubmission"] = 0.0;
  }
  // solution must be submit during offlinecomputation or onlincomputation
  

  if(newSolution["TimeUnitOfSubmission"] != -2 or simulationState==offlineEnd){
    //std::cout << "try acquire lock >17<";  
    vrpApiMutex.lock();
    //std::cout << "tryit >17<\n";
    //std::cout << " updateBestSolution :: TU " << newSolution["TimeUnitOfSubmission"] << std::endl;
    if(messagesToSimulator.empty()){
      //std::cout << " updateBestSolution :: before set value " << std::endl;
      messageToSend.set_value(true);
      //std::cout << " updateBestSolution :: after set value \n";
    }
    json jsonMsg = "{}"_json;
    jsonMsg["messageType"] = "updateBestSolution";
    jsonMsg["solution"] = newSolution;
    messagesToSimulator.push(jsonMsg);
    //std::cout << "----------------> unlock >17<\n";
    vrpApiMutex.unlock();
    
    return true;
  }else{
    return false;
  }
  
}

void vrpApi::updateSimulationState(double currentTU){
  double elapsedSeconds = 0.0;
  switch(simulationState){
      case preSimulation:
        std::cout << "ERROR :: function updateSimulationState called\n";
        std::cout << "         but the simulation is in state preSimulation\n";
        break;

      case offlineComputation:
        currentTime = std::chrono::system_clock::now();
        elapsedSeconds = std::chrono::duration_cast<std::chrono::nanoseconds> (currentTime-startOffline).count();
        elapsedSeconds = elapsedSeconds/1000000000;
        currentTU = -1.0 + (elapsedSeconds - totalPauseTime)/(double)vrpInstance["OfflineTime"];
        if(currentTU >= 0){
          //std::cout << "try acquire lock >18<";
          vrpApiMutex.lock();
          //std::cout << "tryit >18<\n";
          // if not empty, the promise is set. reset will cause an error
          simulationState = offlineEnd;
          // if(messagesToSimulator.empty()){
          //   messageToSend.set_value(true);
          // }
          // json jsonMsg = "{}"_json;
          // jsonMsg["messageType"] = "endOffline";
          // messagesToSimulator.push(jsonMsg);
          //std::cout << "----------------> unlock >18<\n";
          vrpApiMutex.unlock();
          
        }
        break;

      case offlinePause:
        std::cout << "ERROR :: function updateSimulationState called\n";
        std::cout << "         but the simulation is in state offlinePause\n";
        break;

      case offlineEnd:
        std::cout << "ERROR :: function updateSimulationState called\n";
        std::cout << "         but the simulation is in state offlineEnd\n";
        break;

      case onlineComputation:
        currentTime = std::chrono::system_clock::now();
        elapsedSeconds = std::chrono::duration_cast<std::chrono::nanoseconds> (currentTime-startOnline).count();
        elapsedSeconds = elapsedSeconds/1000000000;
        currentTU = (elapsedSeconds - totalPauseTime)/(double)vrpInstance["ComputationTime"];
        if(currentTU > horizonSize){
          // fin du online, on change d'état
          //std::cout << "try acquire lock >19<";
          vrpApiMutex.lock();
          //std::cout << "tryit >19<\n";
          simulationState = onlineEnd;
          if(messagesToSimulator.empty()){
            // si besoin, notifier RunServer d'envoyer un message au simulateur
            //std::cout << " updateSimulationState ::endOnline before set value \n";
            messageToSend.set_value(true);
            //std::cout << " updateSimulationState ::endOnline after set value \n";
          }
          json jsonMsg = "{}"_json;
          jsonMsg["messageType"] = "endOnline";
          messagesToSimulator.push(jsonMsg);
          //std::cout << "----------------> unlock >19<\n";
          vrpApiMutex.unlock();
          
        }
        break;

      case onlinePause:
        std::cout << "ERROR :: function updateSimulationState called\n";
        std::cout << "         but the simulation is in state onlinePause\n";
        break;

      case onlineEnd:
        std::cout << "ERROR :: function updateSimulationState called\n";
        std::cout << "         but the simulation is in state onlineEnd\n";
        break;

      default:
        std::cout << "ERROR :: function updateSimulationState called\n";
        std::cout << "         but the simulation state could not be determined\n";
        break;
    }
}


bool vrpApi::testConnection(){
  std::this_thread::sleep_for(std::chrono::milliseconds(500));
  SolverMessagesImpl sender(grpc::CreateChannel(
        "localhost:" + std::to_string(simulatorPort), grpc::InsecureChannelCredentials()));

    return sender.testConnection();
  return false;
}



void vrpApi::readyForOffline(){

  switch(simulationState){
      case preSimulation:
        break;
      case offlineComputation:
        std::cout << "ERROR :: function readyForOffline called\n";
        std::cout << "         but the simulation is in state offlineComputation\n";
        break;
      case offlinePause:
        std::cout << "ERROR :: function readyForOffline called\n";
        std::cout << "         but the simulation is in state offlinePause\n";
        break;
      case offlineEnd:
        std::cout << "ERROR :: function readyForOffline called\n";
        std::cout << "         but the simulation is in state offlineEnd\n";
        break;
      case onlineComputation:
        std::cout << "ERROR :: function readyForOffline called\n";
        std::cout << "         but the simulation is in state onlineComputation\n";
        break;
      case onlinePause:
        std::cout << "ERROR :: function readyForOffline called\n";
        std::cout << "         but the simulation is in state onlinePause\n";
        break;
      case onlineEnd:
        std::cout << "ERROR :: function readyForOffline called\n";
        std::cout << "         but the simulation is in state onlineEnd\n";
        break;
      default:
        std::cout << "ERROR :: function readyForOffline called\n";
        std::cout << "         but the simulation state could not be determined\n";
        break;
  }
  //std::cout << "try acquire lock >20<";
  vrpApiMutex.lock();
  //std::cout << "tryit >20<\n";
  isReadyForOffline = true;
  //std::cout << "----------------> unlock >20<\n";
  vrpApiMutex.unlock();
  
  auto f = vrpApiOfflineSimulationStarted.get_future();
  f.wait();

  bool startTimeReached = false;
  while(not startTimeReached){
    currentTime = std::chrono::system_clock::now();
    double timeDiff = std::chrono::duration_cast<std::chrono::nanoseconds> (currentTime-startOffline).count();
    if(timeDiff > 0.0){
      startTimeReached = true;
      simulationState = offlineComputation;
    }
  }
}

void vrpApi::readyForOnline(){
  //std::cout << "\nreadyForOnlnie\n";
  //std::cout << "try acquire lock >ready<";
  vrpApiMutex.lock();
  //std::cout << "tryit >ready<\n";
  // if not empty, the promise is set. reset will cause an error
  simulationState = offlineEnd;
  //std::cout << "    is messageTosend empty ? \n";
  if(messagesToSimulator.empty()){
    //std::cout << "    it was empty  \n";
    messageToSend.set_value(true);
  }
  json jsonMsg = "{}"_json;
  jsonMsg["messageType"] = "endOffline";
  messagesToSimulator.push(jsonMsg);
  //std::cout << "----------------> unlock >ready<\n";
  vrpApiMutex.unlock();

  switch(simulationState){
      case preSimulation:
        std::cout << "ERROR :: function readyForOnline called\n";
        std::cout << "         but the simulation is in state preSimulation\n";
        break;
      case offlineComputation:
        //std::cout << "ERROR :: function readyForOnline called\n";
        //std::cout << "         but the simulation is in state offlineComputation\n";
        break;
      case offlinePause:
        std::cout << "ERROR :: function readyForOnline called\n";
        std::cout << "         but the simulation is in state offlinePause\n";
        break;
      case offlineEnd:
        break;
      case onlineComputation:
        std::cout << "ERROR :: function readyForOnline called\n";
        std::cout << "         but the simulation is in state onlineComputation\n";
        break;
      case onlinePause:
        std::cout << "ERROR :: function readyForOnline called\n";
        std::cout << "         but the simulation is in state onlinePause\n";
        break;
      case onlineEnd:
        std::cout << "ERROR :: function readyForOnline called\n";
        std::cout << "         but the simulation is in state onlineEnd\n";
        break;
      default:
        std::cout << "ERROR :: function readyForOnline called\n";
        std::cout << "         but the simulation state could not be determined\n";
        break;
  }
  //std::cout << "try acquire lock >21<";
  vrpApiMutex.lock();
  //std::cout << "tryit >21<\n";
  isReadyForOnline = true;
  totalPauseTime = 0.0;
  //std::cout << "----------------> unlock >21<\n";
  vrpApiMutex.unlock();
  
  auto f = vrpApiOnlineSimulationStarted.get_future();
  f.wait();

  bool startTimeReached = false;
  while(not startTimeReached){
    currentTime = std::chrono::system_clock::now();
    double timeDiff = std::chrono::duration_cast<std::chrono::nanoseconds> (currentTime-startOnline).count();
    if(timeDiff > 0.0){
      startTimeReached = true;
      simulationState = onlineComputation;
    }
  }
}


void *vrpApi::RunServer(void *serverArg) {
  vrpApi *myApi;
  myApi = (vrpApi *) serverArg;
  // Create the server listening to the simulator here
  std::string server_address("0.0.0.0:"+std::to_string(myApi->solverPort));
  SimulatorMessagesHandler service;
  service.smhAPI = myApi;

  ServerBuilder builder;
  // Listen on the given address without any authentication mechanism.
  builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
  // Register "service" as the instance through which we'll communicate with
  // clients. In this case it corresponds to an *synchronous* service.
  builder.RegisterService(&service);
  // Finally assemble the server.
  std::unique_ptr<Server> server(builder.BuildAndStart());

  bool keepLooping = true;
  while(keepLooping){
    bool dataToSend = true;
    std::string dataType;
    json data;
    auto msgToSend = myApi->messageToSend.get_future();
    msgToSend.wait();
    keepLooping = msgToSend.get();
    //std::cout << "  RunServer:: value of keeplooping " << keepLooping << std::endl;


    while(dataToSend){

      // pop the message from the queue
      // and determine what shall be done with dataType
      //std::cout << "try acquire lock >22<";
      myApi->vrpApiMutex.lock();
      //std::cout << "tryit >22<\n";
      if (not myApi->messagesToSimulator.empty()){
        data = myApi->messagesToSimulator.front();
        myApi->messagesToSimulator.pop();
        dataType = data["messageType"];
        if (myApi->messagesToSimulator.empty()){
          // this if is necessary because the queue can be emptied
          // when poping a request just above
          dataToSend = false;
          myApi->messageToSend = std::promise<bool>{};
        }
      }
      else if (myApi->messagesToSimulator.empty()){
        // else the queue is empty
        dataType = "messagesToSimulatorEmpty";
        dataToSend = false;
        myApi->messageToSend = std::promise<bool>{};
      }
      //std::cout << "----------------> unlock >22<\n";
      myApi->vrpApiMutex.unlock();
      


      SolverMessagesImpl sender(grpc::CreateChannel(
            "localhost:" + std::to_string(myApi->simulatorPort), grpc::InsecureChannelCredentials()));
       //std::cout << "vrpAPI.cc :: test the sring : >" << dataType  <<"<";
      if(!dataType.compare("acceptedRequest")){
        // std::cout << " was  acceptedRequest\n";
        sender.acceptRequest(data["request"].dump());

      }else if(!dataType.compare("updateBestSolution")){
        //std::cout << data["solution"]["TimeUnitOfSubmission"] << std::endl;
        sender.sendBestSolution(data["solution"].dump());    

      }else if(!dataType.compare("endOffline")){
        //std::cout << " ------------was  endOffline\n\n\n";
        sender.notifyEndOffline();

      }else if(!dataType.compare("endOnline")){
        // std::cout << " was endOnline\n";
        sender.notifyEndOnline();

      }else if(!dataType.compare("messagesToSimulatorEmpty")){
        // std::cout << "it was  messagesToSimulatorEmpty\n";
        (void) 0;
      }else{
        std::cout << "vrpAPI.cc :: UNEXPECTED MESSAGE  : >" << dataType  <<"<\n";
      }
    }
    //std::cout << "try acquire lock >23<";
    myApi->vrpApiMutex.lock();
    //std::cout << "tryit >23<\n";
    keepLooping = not myApi->endSimulation;
    //std::cout << "----------------> unlock >23<\n";
    myApi->vrpApiMutex.unlock();
    

    // std::cout << "  RunServer :: out of while(dataToSend) \n";
  }
  // std::cout << "  RunServer :: out of while(keepLooping) \n";
  // Wait for the server to shutdown. Note that some other thread must be
  // responsible for shutting down the server for this call to ever return.
  auto f = myApi->vrpApiexit_requested.get_future();
  f.wait();
  server->Shutdown();

  //void *status;
  //int rc = pthread_join(listenerThread, &status);
  //if (rc) {
  //  std::cout << "Error:unable to join listenerThread, " << rc << std::endl;
  //  exit(-1);
  //}
  pthread_exit(NULL);
}


