#include <unistd.h>
#include <string.h>

#include <iostream>
#include <string>
#include <thread>
#include <mutex>

#include "../../../source/utils/common/time.h"

using namespace std;
using namespace balance::util;

mutex _lock;

__global__
void saxpy(int n, float a, float *x, float *y)
{
	int i = blockIdx.x * blockDim.x + threadIdx.x;
	if (i < n) y[i] = a * x[i] + y[i];
}

void func1(void) {
	int N = 1 << 25;
	float *x, *y, *d_x, *d_y;
	x = (float*)malloc(N * sizeof(float));
	y = (float*)malloc(N * sizeof(float));

	cudaMalloc(&d_x, N * sizeof(float)); 
	cudaMalloc(&d_y, N * sizeof(float));

	for (int i = 0; i < N; i++) {
		x[i] = 1.0f;
		y[i] = 2.0f;
	}

	cudaMemcpy(d_x, x, N * sizeof(float), cudaMemcpyHostToDevice);
	cudaMemcpy(d_y, y, N * sizeof(float), cudaMemcpyHostToDevice);

	_lock.lock();
	cout << "func1 locks" << endl;
	usleep(2000);

    double time_1 = time_now();
    for (int i = 0; i < 1000; ++i) {
        saxpy<<<(N + 255) / 256, 256>>>(N, 2.0f, d_x, d_y);
    }
    // cudaDeviceSynchronize();
    double time_2 = time_now();
    double latency = time_2 - time_1;
    cout << "Latency for computation: " << fixed << latency << endl;

	cudaMemcpy(y, d_y, N * sizeof(float), cudaMemcpyDeviceToHost);

	float maxError = 0.0f;
	for (int i = 0; i < N; i++)
		maxError = max(maxError, abs(y[i] - 2.0f * 1001));
	cout << "Max error: " << fixed << maxError << endl;

	cudaFree(d_x);
	cudaFree(d_y);
	free(x);
	free(y);
}

void func2(void) {
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

	_lock.unlock();
	// sleep(1);
	cout << "func2 unlocks" << endl;

	double time_1, time_2, latency;
	time_1 = time_now();
	cudaError_t e;
	e = cudaHostRegister(x, N * sizeof(float), cudaHostRegisterDefault);
	cout << cudaGetErrorString(e) << endl;
	e = cudaHostRegister(y, N * sizeof(float), cudaHostRegisterDefault);
	cout << cudaGetErrorString(e) << endl;
    time_2 = time_now();
    latency = time_2 - time_1;
	cout << "Latency for pin: " << fixed << latency << endl;

	time_1 = time_now();
    cudaMemcpyAsync(d_x, x, N * sizeof(float), cudaMemcpyHostToDevice, stream1);
	cudaMemcpyAsync(d_y, y, N * sizeof(float), cudaMemcpyHostToDevice, stream1);
    time_2 = time_now();
    latency = time_2 - time_1;
	cout << "Latency for tranmission: " << fixed << latency << endl;

	sleep(1);
	cudaFree(d_x);
	cudaFree(d_y);
	free(x);
	free(y);
	// cudaFreeHost(x);
	// cudaFreeHost(y);
}

int main(void) {
	_lock.lock();
	cout << "Locked" << endl;
	sleep(1);

	// Start thread 1
	thread t1(func1);
	sleep(1);

	// Start thread 2
	thread t2(func2);
	sleep(1);

	// Join
	t1.join();
	t2.join();

	return 0;
}