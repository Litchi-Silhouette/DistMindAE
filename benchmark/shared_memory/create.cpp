#include <unistd.h>
#include <stdlib.h>
#include <string.h>

#include <iostream>
#include <string>

#include "../../source/utils/shared_memory/shared_memory.h"
#include "../../source/utils/tcp/tcp.h"
#include "../../source/utils/common/time.h"

using namespace std;
using namespace balance::util;

int main(int argc, char** argv) {
    if (argc < 3) {
        cout << "Arguments Error" << endl;
        return 1;
    }
    string prefix(argv[1]);
    size_t size = atol(argv[2]);

    double total_latency = 0.0;
    double max_latency = 0.0;
    for (int i = 0; i < 100; ++i) {
        string name(prefix + "-" + to_string(i));
        double time_1 = time_now();
        SharedMemory shm(name, size, true);
        double time_2 = time_now();
        memset(shm.getPointer(), 0, shm.getSize());
        double latency = time_2 - time_1;
        total_latency += latency;
        max_latency = max(latency, max_latency);
        cout << "Create shared memory latency: " << fixed  << latency << endl;
    }
    cout << "Average latency: " << fixed << total_latency / 100 << endl;
    cout << "Max latency: " << fixed  << max_latency << endl;

    return 0;
}