// Приклад дивергентного коду (C / CUDA C)
__global__ void process_elements(float *output, const float *input, int threshold)
{
    int tid = threadIdx.x;
    float value = input[tid];

    if (value > threshold) {
        // Гілка A: тривале математичне обчислення
        output[tid] = sqrtf(value) * logf(value) + expf(value * 0.1f);
    } else {
        // Гілка B: швидке обнулення
        output[tid] = 0.0f;
    }
}
