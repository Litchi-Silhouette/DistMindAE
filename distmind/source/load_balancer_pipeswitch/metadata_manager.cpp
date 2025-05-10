#include <unistd.h>

#include <string>
#include <iostream>
#include <fstream>
#include <memory>
#include <vector>

#include "metadata_manager.h"
#include "tcp.h"

using namespace std;

MetadataManager::MetadataManager(string server_list_filename) {
    ifstream server_list(server_list_filename);
    string address;
    while (server_list >> address)
        registerServer(address);
}

vector<string> MetadataManager::getServerAddresses() {
    vector<string> res;
    for (auto itr = _workload_info.begin(); itr != _workload_info.end(); ++itr)
        res.push_back(itr->first);
    return res;
}

void MetadataManager::registerServer(string address) {
    const lock_guard<mutex> guard(_lock);
    _workload_info[address] = 0;
}

void MetadataManager::setServerPreference(string address, string model_name) {
    const lock_guard<mutex> guard(_lock);
    bool inference = (model_name.find("inference") != string::npos);
    if (inference)
        _inference_servers.insert(address);
    else
        _inference_servers.erase(address);
}

// void MetadataManager::increaseWorkload(int ip_int, int port, string model_name) {
//     const lock_guard<mutex> guard(_lock);
//     _workload_info[ip_int][port]++;
//     // cout << "Cache Liveness" << ", " << (unsigned int)ip_int << ", " << model_name << ", " << _cache_active[ip_int][model_name] << endl;
// }
void MetadataManager::decreaseWorkload(string address) {
    const lock_guard<mutex> guard(_lock);
    _workload_info[address]--;
    // cout << "Cache Liveness" << ", " << (unsigned int)ip_int << ", " << model_name << ", " << _cache_active[ip_int][model_name] << endl;
}

string MetadataManager::forwardToLeastLoadedServer(string model_name, int threshold) {
    const lock_guard<mutex> guard(_lock);
    bool inference = (model_name.find("inference") != string::npos);

    string address;
    int minimum_workload = threshold + 1;
    for (auto itr = _workload_info.begin(); itr != _workload_info.end(); ++itr) {
        bool match = (_inference_servers.find(itr->first) != _inference_servers.end()) == inference;
        if (match && itr->second < minimum_workload) {
            address = itr->first;
            minimum_workload = itr->second;
        }
    }
    _workload_info[address]++;

    return address;
}