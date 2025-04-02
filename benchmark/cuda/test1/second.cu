#include <unistd.h>

#include <iostream>
#include <string>

#include "../../source/utils/common/time.h"
#include "../../source/utils/tcp/tcp.h"

using namespace std;
using namespace balance::util;

__global__
void saxpy(int n, float a, float *x, float *y)
{
	int i = blockIdx.x * blockDim.x + threadIdx.x;
	if (i < n) y[i] = a * x[i] + y[i];
}

int main(void) {
	TcpClient client(string("127.0.0.1"), 7777);

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

	char buffer[8];
	memset(buffer, 0, 8);
	client.tcpRecv(buffer, 4);
	memcpy(buffer, "WXYZ", 4);
	client.tcpSend(buffer, 4);
	usleep(2000);

    double time_1 = time_now();
    for (int i = 0; i < 1000; ++i) {
        saxpy<<<(N + 255) / 256, 256>>>(N, 2.0f, d_x, d_y);
    }
    // cudaDeviceSynchronize();
    double time_2 = time_now();
    double latency = time_2 - time_1;
    cout << "Latency: " << fixed << latency << endl;

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