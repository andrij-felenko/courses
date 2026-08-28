// Код із потенційною дивергенцією варпу (C++)
#include <cuda_runtime.h>

__global__ void process_data(float *data, int n)
{
    const int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid >= n) {
        return;
    }

    if (tid < 16) {
        data[tid] = data[tid] * 2.0f; // Гілка THEN
    } else {
        data[tid] = data[tid] + 5.0f; // Гілка ELSE
    }
}
