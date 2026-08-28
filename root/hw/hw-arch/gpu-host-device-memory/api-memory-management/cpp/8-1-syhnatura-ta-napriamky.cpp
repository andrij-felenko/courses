/* C++ безпечна обгортка неблокуючого копіювання */
#include <cuda_runtime.h>
#include <stdexcept>

inline void async_copy(void* dst, const void* src, size_t bytes, cudaMemcpyKind kind, cudaStream_t stream) {
    cudaError_t err = cudaMemcpyAsync(dst, src, bytes, kind, stream);
    if (err != cudaSuccess) {
        throw std::runtime_error("cudaMemcpyAsync failed");
    }
}
