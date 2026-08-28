/* C++ обгортка автоматичної пам'яті з префетчингом */
#include <cuda_runtime.h>
#include <stdexcept>

template <typename T>
class ManagedBuffer {
public:
    explicit ManagedBuffer(size_t count, unsigned int flags = cudaMemAttachGlobal) 
        : count_(count) {
        cudaError_t err = cudaMallocManaged(reinterpret_cast<void**>(&ptr_),
                                            count_ * sizeof(T),
                                            flags);
        if (err != cudaSuccess) {
            throw std::runtime_error("cudaMallocManaged failed");
        }
    }
    ~ManagedBuffer() noexcept {
        if (ptr_) cudaFree(ptr_);
    }

    void prefetch_to_device(int device_id, cudaStream_t stream = 0) {
        cudaMemPrefetchAsync(ptr_, count_ * sizeof(T), device_id, stream);
    }
    void prefetch_to_host(cudaStream_t stream = 0) {
        cudaMemPrefetchAsync(ptr_, count_ * sizeof(T), cudaCpuDeviceId, stream);
    }

    [[nodiscard]] T* data() noexcept { return ptr_; }
    [[nodiscard]] size_t size() const noexcept { return count_; }

private:
    T *ptr_{nullptr};
    size_t count_{0};
};
