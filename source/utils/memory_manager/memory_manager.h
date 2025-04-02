#ifndef BALANCE_MEMORY_MANAGER_H
#define BALANCE_MEMORY_MANAGER_H

#include <unistd.h>

#include <string>
#include <memory>
#include <queue>
#include <vector>
#include <mutex>

#include "utils/shared_memory/shared_memory.h"
#include "utils/common/pointer.h"

namespace balance {
namespace util {

struct BlockGroup {
    size_t num;
    size_t size;
    OffsetPointer data0;

    std::vector<OffsetPointer> accessFraction(size_t target_offset, size_t target_size);
};

class MemoryManager {
public:
    MemoryManager(std::string shm_name, size_t shm_size, size_t block_size);
    ~MemoryManager();
    std::string getShmName();
    size_t getShmSize();
    char* getShmPointer();
    std::shared_ptr<BlockGroup> allocate(size_t size);
    void deallocate(std::shared_ptr<BlockGroup> bg);
    size_t getBlockAvailable();
private:
    size_t _block_size;
    std::shared_ptr<SharedMemory> _shm;
    std::queue<size_t> _block_pool;
};

} //namespace util
} //namespace balance

#endif