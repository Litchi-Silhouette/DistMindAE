#include <unistd.h>
#include <string.h>

#include <iostream>
#include <string>

#include "../../source/utils/common/time.h"
#include "../../source/utils/tcp/tcp.h"

using namespace std;
using namespace balance::util;

int main(void) {
	TcpServer server(string("0.0.0.0"), 7777);
	TcpAgent agent = server.tcpAccept();

	int N = 1 << 25;
	float *x, *y, *d_x, *d_y;
	x = (float*)malloc(N * sizeof(float));
	y = (float*)malloc(N * sizeof(float));
	// cudaHostAlloc((void**)&x, N * sizeof(float), cudaHostAllocDefault);
	// cudaHostAlloc((void**)&y, N * sizeof(float), cudaHostAllocDefault);

	cudaStream_t stream1;
	cudaStreamCreate(&stream1);
	cudaMalloc(&d_x, N * sizeof(float)); 
	cudaMalloc(&d_y, N * sizeof(float));

	for (int i = 0; i < N; i++) {
		x[i] = 1.0f;
		y[i] = 2.0f;
	}

	char buffer[8];
	memset(buffer, 0, 8);
	memcpy(buffer, "ABCD", 4);
	agent.tcpSend(buffer, 4);
	agent.tcpRecv(buffer, 4);
	cout << buffer << endl;

	double time_1, time_2, latency;
	time_1 = time_now();
	cudaError_t e;
	e = cudaHostRegister(x, N * sizeof(float), cudaHostRegisterDefault);
	cout << cudaGetErrorString(e) << endl;
	e = cudaHostRegister(y, N * sizeof(float), cudaHostRegisterDefault);
	cout << cudaGetErrorString(e) << endl;
    time_2 = time_now();
    latency = time_2 - time_1;
	cout << "Latency: " << fixed << latency << endl;

	time_1 = time_now();
    cudaMemcpyAsync(d_x, x, N * sizeof(float), cudaMemcpyHostToDevice, stream1);
	cudaMemcpyAsync(d_y, y, N * sizeof(float), cudaMemcpyHostToDevice, stream1);
    time_2 = time_now();
    latency = time_2 - time_1;
	cout << "Latency: " << fixed << latency << endl;

	sleep(1);
	cudaFree(d_x);
	cudaFree(d_y);
	free(x);
	free(y);
	// cudaFreeHost(x);
	// cudaFreeHost(y);
}