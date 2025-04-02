#ifndef CLI_COMM_H
#define CLI_COMM_H

#include "spdlog/spdlog.h"
#include "utils/utils.h"

void* openSHM(std::string& shmName, size_t& shmSize){
  int data_fd = shm_open(shmName.c_str(), O_CREAT | O_RDWR, 0666);
  pipeps::store::check_err((ftruncate(data_fd, shmSize) < 0), "ftruncate instr_fd err\n");
  void* data_buf_ptr =
      mmap(0, shmSize, PROT_READ | PROT_WRITE, MAP_SHARED, data_fd, 0);
  return data_buf_ptr;
};

void reportBandwidth(size_t& len, double& s, double& e) {
  double dur = e - s;
  double bw = ((len * 8) / dur) / 1e9;
  spdlog::info("bw: {:f} Gbps; dur: {:f}", bw, dur);
}

void gen_random(char *s, const int len) {
    static const char alphanum[] =
        "0123456789"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz";

    for (int i = 0; i < len; ++i) {
        s[i] = alphanum[rand() % (sizeof(alphanum) - 1)];
    }

    s[len] = 0;
}

#endif