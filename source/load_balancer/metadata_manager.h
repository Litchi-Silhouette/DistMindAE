#ifndef BALANCE_LB_METADATA_MANAGER_H
#define BALANCE_LB_METADATA_MANAGER_H

#include <unistd.h>

#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <list>

#include "utils/utils.h"

// Reference: https://www.geeksforgeeks.org/lru-cache-implementation/
class LRUCacheForString {
public:
    LRUCacheForString() {};
    LRUCacheForString(const LRUCacheForString &lru);
    ~LRUCacheForString() {};
    LRUCacheForString operator=(const LRUCacheForString &lru);
    void push(std::string model_name);
    void finish(std::string model_name);
    std::string pop();

private:
    std::list<std::string> _order;
    std::unordered_map<std::string, size_t> _ref_counter;
    std::unordered_map<std::string, std::list<std::string>::iterator> _location;
};

class MetadataManager {
public:
    MetadataManager() {};
    ~MetadataManager() {};

    void register_cache(int ip_int, size_t capacity);
    void register_server(int ip_int, int port);

    const std::unordered_map<std::string, std::unordered_set<int> >& get_cache_location();
    const std::unordered_map<int, std::unordered_map<int, int> >& get_workload();

    size_t get_cache_limit(int ip_int);
    size_t get_cache_used(int ip_int);
    size_t get_model_size(std::string model_name);
    void set_model_size(std::string model_name, size_t size);
    bool check_cache(int ip_int, std::string model_name);
    void cache_in_model(int ip_int, std::string model_name);
    std::string cache_out_model(int ip_int);

    void increase_workload(int ip_int, int port, std::string model_name);
    void decrease_workload(int ip_int, int port, std::string model_name);
    int check_idle_server();

private:
    std::unordered_map<std::string, size_t> _model_size; // Map: model_name -> size of model parameters
    std::unordered_map<int, size_t> _cache_limit; // Map: ip_int -> allocated memory of caches
    std::unordered_map<int, size_t> _cache_used; // Map: ip_int -> used memory of caches
    
    // AtomicLRUCacheForString _lru_cache_all;
    std::unordered_map<int, LRUCacheForString> _lru_cache_each; // Map: ip_int -> LRUCache for models
    std::unordered_map<std::string, std::unordered_set<int> > _cache_location; // Map: model_name -> list of ip_int
    
    std::unordered_map<int, std::unordered_map<int, int> > _workload_info; // Map: ip_int -> workload of each port
};

#endif