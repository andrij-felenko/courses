/* C++ обгортка конфігурації пулу пам'яті */
#include <cuda_runtime.h>
#include <stdexcept>

inline void configure_pool(cudaMemPool_t pool, uint64_t release_threshold_bytes) {
    cudaError_t err = cudaMemPoolSetAttribute(pool, 
                                              cudaMemPoolAttrReleaseThreshold, 
                                              &release_threshold_bytes);
    if (err != cudaSuccess) {
        throw std::runtime_error("cudaMemPoolSetAttribute failed");
    }
}
