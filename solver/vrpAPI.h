#ifndef VRPAPI_H
#define VRPAPI_H

#include <chrono>
#include <condition_variable>
#include <thread>
#include <pthread.h>
#include <queue>
#include <string>
#include "json.hpp"
#include <iostream>
#include <memory>
#include <vector>
#include <string>
#include <mutex>



#include <future>
#include <fstream>
#include "json.hpp"

using json = nlohmann::json;


#include <grpc++/grpc++.h>


#include "vrpAPI.grpc.pb.h"

#include "vrpAPI.pb.h"



using grpc::Channel;
using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::ClientContext;
using grpc::Status;

using vrpAPI::SimulatorMessages;
using vrpAPI::JsonMessage;
using vrpAPI::TimeUnitMessage;
using vrpAPI::Empty;
using vrpAPI::BoolMessage;
using vrpAPI::DoubleMessage;

using vrpAPI::SolverMessages;


using json = nlohmann::json;




class vrpApi{
public:
	// Constructor, Users do not need to use it
	vrpApi();

	/*--------------------------------------

		Here Below, you will find all the useful functions
		for you solver. 

	--------------------------------------*/


	// not used anymore ? 
	bool acceptRequest(json request, bool accept);

	// return the current time unit of the simulation.
	// A negative value means the simulation is in the
	// offline computation time.
	double getCurrentTimeUnit();

	// return the current state of the simulation 
	std::string getCurrentSimulationState();

	// return a json object that is the last solution sent by the simulator
	// return an empty json object if no solution was sent
	json getNewCurrentSolution();

	// return an json object containing all the data of the problem
	// Carrier, Customers, Graph etc...
	json getVrpData();

	// return True if the Simulator send a solution, false otherwise
	// this solution is the last solution considered valid
	bool isNewCurrentSolution();

	// return true if new requests wait to be popped with popNewRequest
	bool isNewRequests();

	// Blocks the solver thread if the simulator asked to pause the solver
	// Unblocks the solver thread when the simulator ask to continue
	void pauseIfSimulatorAsks();

	// Return the oldest request sent by the simulator that was not yet
	// pop by this function.
	// Return an empty json object if no requests in the queue
	// All the requests sent by the simulator are stored in a FIFO queue
	// This function pop the request out of the queue
	json popNewRequest();

	// This function is used to synchronized the simulator and the solver.
	// This function blocks the solver until the start of the simulation.
	// The simulator can not start the simulation before the solver call
	// this function.
	//void ready();


	void readyForOffline();

	void readyForOnline();

	// function that start the tread listening to the simulator
	// It is impossible to receive data from the simulator before
	// calling this function
	void startListeningSimulator(bool verboseAPI);

	// return true if it can reach the simulator, otherwise false
	bool testConnection();

	// send the newSolution to be used to the Solver
	bool updateBestSolution(json newSolution);

	//
	void updateSimulationState(double currentTU);

	// true if new data arrived from the simulator since the last call of getVrpData()
	bool vrpDataChanged();




	/*--------------------------------------

		Variables for background processes.

	--------------------------------------*/

	
	
	std::recursive_mutex vrpApiMutex;
	std::mutex pauseMutex;
	std::promise<void> vrpApiexit_requested;
	std::promise<void> vrpApiSimulationStarted;
	std::promise<void> vrpApiOfflineSimulationStarted;
	std::promise<void> vrpApiOnlineSimulationStarted;

	std::promise<bool> messageToSend;

	std::promise<double> beginPause;
	std::promise<void> endPause;

	std::chrono::time_point<std::chrono::system_clock> start, currentTime;
	std::chrono::time_point<std::chrono::system_clock> startPauseTime, endPauseTime;
	double totalPauseTime;

	std::chrono::time_point<std::chrono::system_clock> startOffline, startOnline;
	
	bool askPause;
	bool inPause;

	int currentTU;
	json simulatorSolution;
	bool newSimulatorSolution;
	bool dataChanged;
	bool endSimulation;
	pthread_t listenerThread;
	std::queue<json> newRequestQueue;
	int numberOfSolutions;
	int horizonSize;
	bool isready;
	bool isReadyForOffline;
	bool isReadyForOnline;
	bool simulationStarted;

	bool offlineSimulationStarted;
	bool onlineSimulationStarted;

	int  simulatorPort;
	int  solverPort;
	bool verbose;
	json vrpInstance;


	std::queue<json> messagesToSimulator;
	//std::queue<json> solutionsToSend;
	//std::queue<json> acceptedRequests;

	enum stateOfSimulation {preSimulation, offlineComputation, offlinePause, offlineEnd, onlineComputation, onlinePause, onlineEnd};

	enum stateOfSimulation simulationState;
private:
	static void *RunServer(void*);
};


#endif


