/* C++ функція отримання пристрою поточної локації пам'яті */
#include <cuda_runtime.h>
#include <stdexcept>

inline int query_last_prefetch_device(const void* ptr, size_t bytes) {
    int dev_id = -1;
    cudaError_t err = cudaMemRangeGetAttribute(&dev_id, sizeof(int),
                                               cudaMemRangeAttributeLastPrefetchLocation,
                                               ptr, bytes);
    if (err != cudaSuccess) {
        throw std::runtime_error("cudaMemRangeGetAttribute failed");
    }
    return dev_id;
}
