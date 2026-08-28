// Код із потенційною дивергенцією варпу (C)
__global__ void process_data(float *data, int n)
{
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid >= n) return;

    if (tid < 16) {
        data[tid] = data[tid] * 2.0f; // Гілка THEN
    } else {
        data[tid] = data[tid] + 5.0f; // Гілка ELSE
    }
}
