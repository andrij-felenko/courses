/* C++: обгортка Unified Memory з автоматичним префетчингом */
#include <cuda_runtime.h>
#include <stdexcept>

template <typename T>
class PrefetchedManagedMemory {
public:
    explicit PrefetchedManagedMemory(size_t count) : count_(count) {
        cudaError_t err = cudaMallocManaged(reinterpret_cast<void**>(&ptr_),
                                            count_ * sizeof(T),
                                            cudaMemAttachGlobal);
        if (err != cudaSuccess) {
            throw std::runtime_error("cudaMallocManaged failed");
        }
    }
    ~PrefetchedManagedMemory() noexcept {
        if (ptr_) cudaFree(ptr_);
    }

    void prefetch_to_gpu(int device_id, cudaStream_t stream = 0) {
        cudaMemPrefetchAsync(ptr_, count_ * sizeof(T), device_id, stream);
    }

    void prefetch_to_cpu(cudaStream_t stream = 0) {
        cudaMemPrefetchAsync(ptr_, count_ * sizeof(T), cudaCpuDeviceId, stream);
    }

    [[nodiscard]] T* data() noexcept { return ptr_; }
    [[nodiscard]] size_t size() const noexcept { return count_; }

private:
    T *ptr_{nullptr};
    size_t count_{0};
};
