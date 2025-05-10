#ifndef BALANCE_LB_METADATA_MANAGER_H
#define BALANCE_LB_METADATA_MANAGER_H

#include <unistd.h>

#include <string>
#include <mutex>
#include <unordered_map>
#include <unordered_set>

struct pair_hash {
    inline std::size_t operator()(const std::pair<int, int> & v) const {
        return (((uint64_t)v.first) << 31) + (uint64_t)v.second;
    }
};

class MetadataManager {
public:
    MetadataManager() {};
    MetadataManager(std::string server_list_filename);

    ~MetadataManager() {};

    std::vector<std::string> getServerAddresses();

    void registerServer(std::string address);
    void setServerPreference(std::string address, std::string model_name);
    // void increaseWorkload(int ip_int, int port, std::string model_name);
    void decreaseWorkload(std::string address);
    std::string forwardToLeastLoadedServer(std::string model_name, int threshold);

private:
    std::unordered_map<std::string, int> _workload_info; // Map: (ip:port) -> workload
    std::unordered_set<std::string> _inference_servers; // Workers for inference
    std::mutex _lock;
};

#endif