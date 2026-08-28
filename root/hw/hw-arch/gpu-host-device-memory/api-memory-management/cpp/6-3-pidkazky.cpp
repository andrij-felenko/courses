/* C++ обгортка конфігурації підказок розміщення пам'яті */
#include <cuda_runtime.h>
#include <stdexcept>

inline void advise_memory(const void* ptr, size_t bytes, cudaMemoryAdvise advice, int device) {
    cudaError_t err = cudaMemAdvise(ptr, bytes, advice, device);
    if (err != cudaSuccess) {
        throw std::runtime_error("cudaMemAdvise failed");
    }
}
