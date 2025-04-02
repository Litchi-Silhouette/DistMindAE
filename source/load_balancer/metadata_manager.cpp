#include <unistd.h>

#include <string>
#include <iostream>

#include "metadata_manager.h"

using namespace std;
using namespace balance::util;

LRUCacheForString::LRUCacheForString(const LRUCacheForString &lru):
_order(lru._order), _location(lru._location) {}

LRUCacheForString LRUCacheForString::operator=(const LRUCacheForString &lru) {
    return LRUCacheForString(lru);
}

void LRUCacheForString::push(string model_name) {
    if (_location.find(model_name) != _location.end())
        _order.erase(_location[model_name]);
    if (_ref_counter.find(model_name) == _ref_counter.end())
        _ref_counter[model_name] = 0;
    _order.push_front(model_name);
    _location[model_name] = _order.begin();
    _ref_counter[model_name]++;
}

void LRUCacheForString::finish(string model_name) {
    _ref_counter[model_name]--;
}

string LRUCacheForString::pop() {
    auto itr = _order.rbegin();
    while (itr != _order.rend() && _ref_counter[*itr] > 0)
        ++itr;

    if (itr != _order.rend()) {
        string model_name = *itr;
        _order.erase(--(itr.base()));
        _location.erase(model_name);
        return model_name;
    }
    else {
        return string("");
    }
}

void MetadataManager::register_cache(int ip_int, size_t capacity) {
    _cache_limit[ip_int] = capacity;
    _cache_used[ip_int] = 0;
    _lru_cache_each[ip_int] = LRUCacheForString();
}

void MetadataManager::register_server(int ip_int, int port) {
    if (_workload_info.find(ip_int) == _workload_info.end())
        _workload_info[ip_int] = unordered_map<int, int>();
    if (_workload_info[ip_int].find(port) == _workload_info[ip_int].end())
        _workload_info[ip_int][port] = 0;
}

const unordered_map<string, unordered_set<int> >& MetadataManager::get_cache_location() {
    return _cache_location;
}
const unordered_map<int, unordered_map<int, int> >& MetadataManager::get_workload() {
    return _workload_info;
}

size_t MetadataManager::get_cache_limit(int ip_int) {
    return _cache_limit[ip_int];
}

size_t MetadataManager::get_cache_used(int ip_int) {
    return _cache_used[ip_int];
}

size_t MetadataManager::get_model_size(std::string model_name) {
    auto itr = _model_size.find(model_name);
    if (itr == _model_size.end())
        return 0;
    else
        return itr->second;
}

void MetadataManager::set_model_size(std::string model_name, size_t size) {
    _model_size[model_name] = size;
}

bool MetadataManager::check_cache(int ip_int, std::string model_name) {
    if (_cache_location.find(model_name) == _cache_location.end())
        return false;
    if (_cache_location[model_name].find(ip_int) == _cache_location[model_name].end())
        return false;
    return true; 
}

void MetadataManager::cache_in_model(int ip_int, string model_name) {
    if (_cache_location[model_name].find(ip_int) == _cache_location[model_name].end())
        _cache_used[ip_int] += get_model_size(model_name) * MEMORY_MANAGER_AMPLIFIER;
    _lru_cache_each[ip_int].push(model_name);
    _cache_location[model_name].insert(ip_int);
}

string MetadataManager::cache_out_model(int ip_int) {
    string model_name = _lru_cache_each[ip_int].pop();
    if (model_name.length() > 0) {
        _cache_location[model_name].erase(ip_int);
        _cache_used[ip_int] -= get_model_size(model_name) * MEMORY_MANAGER_AMPLIFIER;
    }
    return model_name;
}

void MetadataManager::increase_workload(int ip_int, int port, string model_name) {
    _workload_info[ip_int][port]++;
}
void MetadataManager::decrease_workload(int ip_int, int port, string model_name) {
    _workload_info[ip_int][port]--;
    _lru_cache_each[ip_int].finish(model_name);
}
int MetadataManager::check_idle_server() {
    int max_idle = -1024;
    for (auto itr_machine = _workload_info.begin(); itr_machine != _workload_info.end(); ++itr_machine) {
        auto machine_info = itr_machine->second;
        int idle_index = machine_info.size();
        for (auto itr_gpu = machine_info.begin(); itr_gpu != machine_info.end(); ++itr_gpu) {
            idle_index -= itr_gpu->second;
        }
        if (idle_index > max_idle)
            max_idle = idle_index;
    }
    return max_idle;
}