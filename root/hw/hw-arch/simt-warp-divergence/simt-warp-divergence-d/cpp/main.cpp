// Приклад дивергентного коду (Modern CUDA C++)
#include <cuda_runtime.h>
#include <cmath>
#include <span>

namespace gpu {

template <typename T>
__global__ void process_elements(T * __restrict__ output, const T * __restrict__ input, T threshold)
{
    const int tid = threadIdx.x;
    const T value = input[tid];

    if (value > threshold) {
        // Гілка A: тривале обчислення
        output[tid] = std::sqrt(value) * std::log(value) + std::exp(value * static_cast<T>(0.1));
    } else {
        // Гілка B: обнулення
        output[tid] = static_cast<T>(0);
    }
}

} // namespace gpu
