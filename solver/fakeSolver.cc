#include "vrpAPI.h"  
#include <iostream>
#include <chrono>
#include <thread>

int main(int argc, char** argv) {
  // to avoid warning at compilation
  (void) argc;
  (void) argv;

	/* 
    Instantiate the api

		I start to listen to the simulator with this function
		If the simulator tries to send a message before I used this function
		it will get an error
	*/
  vrpApi myVRPAPI;
	myVRPAPI.startListeningSimulator(false);
  std::cout << "fakeSolver:: startListeningSimulator" << std::endl;




  /*
    testConnection return true if the communication with the simulator is ok
    Here, we wait the simulator to be launched
  */
  while(not myVRPAPI.testConnection()){
    std::this_thread::sleep_for(std::chrono::milliseconds(500));
  }
  std::cout << "fakeSolver:: the simulator is connected" << std::endl;

	/* 	
		getVrpData return the data sent by the simulator.

    vrpDataChanged return true if new data arrived since the last call to
    getVrpData.

    Note that we do not check if we received the computation time because
    it is not necessary for the offline simulation.
	*/ 
	json myVRPdata;
  bool dataReceived = false;
  while(not dataReceived){
    if(myVRPAPI.vrpDataChanged()){

      myVRPdata = myVRPAPI.getVrpData();

      if(myVRPdata.find("Carrier")         != myVRPdata.end() and
         myVRPdata.find("Customers")       != myVRPdata.end() and
         myVRPdata.find("Carrier")         != myVRPdata.end() and
         myVRPdata.find("OfflineTime")     != myVRPdata.end()
         ){
          dataReceived = true;
      }
    }
  }
  std::cout << "fakeSolver:: Data Received" << std::endl;

  double OfflineTime = myVRPdata["OfflineTime"];
  std::cout << "fakeSolver:: OfflineTime     :" << OfflineTime << std::endl;


  /*
    readyForOffline() is used to synchronized the simulator and the solver.
    this function notify the simulator that solver is ready to start
    the offline simulation.
    This function blocks until the simulator start the simulation

    getCurrentSimulationState() can be used to know if the offline/online
    simulation is finished or not.
    When the simulation is running, it returns offlineComputation/onlineComputation
    When the offline simulation is finished, it returns offlineEnd
    When the online simulation is finished, it returns onlineEnd
  */
  std::cout << "fakeSolver:: myAPI.readyForOffline()" << std::endl;
  myVRPAPI.readyForOffline();
  while(myVRPAPI.getCurrentSimulationState() == "offlineComputation"){
    myVRPAPI.pauseIfSimulatorAsks();
    std::cout << "  Offline Simulation: current time unit: " << myVRPAPI.getCurrentTimeUnit() << std::endl;
    std::this_thread::sleep_for(std::chrono::milliseconds(1000));
  }
  std::cout << "fakesolver:: finish the loop for offlinesimulation\n";



  /*
    The Offline Simulation is now finished.

    It is now mandatory to have the computation time
    Thus we get it before notify the simulator with 
    the function readyForOnline()
  */
  dataReceived = false;
  if(myVRPdata.find("ComputationTime") != myVRPdata.end()){
          dataReceived = true;
  }
  while(not dataReceived){
    if(myVRPAPI.vrpDataChanged()){

      myVRPdata = myVRPAPI.getVrpData();

      if(myVRPdata.find("ComputationTime") != myVRPdata.end()){
          dataReceived = true;
      }
    }
  }
  std::cout << "fakeSolver:: Data Received" << std::endl;
  double ComputationTime = myVRPdata["ComputationTime"];
  std::cout << "fakeSolver:: ComputationTime :" << ComputationTime << std::endl;



  std::cout << "fakeSolver:: myAPI.readyForOnline()" << std::endl;
  myVRPAPI.readyForOnline();
  std::cout << "fakeSolver:: simulation started" << std::endl;




  json nR;

  /*
    getCurrentTimeUnit() returns the current time unit in double.

    If the number is < 0 , it means the simulation is in the offline time.
  */
  double cu = myVRPAPI.getCurrentTimeUnit();


  while(myVRPAPI.getCurrentSimulationState() == "onlineComputation"){
    myVRPAPI.pauseIfSimulatorAsks();

    // numberNewRequests returns the number of new requests in the queue of the pop function
    while(myVRPAPI.isNewRequests()){
      std::cout << "fakeSolver:: popRequest at" << myVRPAPI.getCurrentTimeUnit() << std::endl;
      // return a new request sent by the simulator
      nR = myVRPAPI.popNewRequest();
      std::cout << nR << std::endl;
    }

    cu = myVRPAPI.getCurrentTimeUnit();
    std::cout << "fakeSolver:: TU: " << cu << std::endl;


    if(cu >= 15.0 and cu <= 16.0){
      json exampleSolution = myVRPdata["Carrier"]["Vehicles"];
      //myVRPAPI.updateBestSolution(exampleSolution);
      //std::cout << "fakeSolver:: first solution sent to the simulator" << std::endl;
    }


    std::this_thread::sleep_for(std::chrono::milliseconds(1000));
  }

  std::cout << "fakeSolver:: End of the solver execution" << std::endl;
  return 0;
}
