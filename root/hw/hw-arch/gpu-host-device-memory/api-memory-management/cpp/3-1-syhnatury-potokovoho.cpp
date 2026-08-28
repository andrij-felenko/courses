/* C++ інтерфейс асинхронного буфера, прив'язаного до життєвого циклу потоку */
#include <cuda_runtime.h>
#include <stdexcept>
#include <string>

template <typename T>
class AsyncDeviceMemory {
public:
    AsyncDeviceMemory(size_t count, cudaStream_t stream) 
        : count_(count), stream_(stream) {
        cudaError_t err = cudaMallocAsync(reinterpret_cast<void**>(&ptr_),
                                          count_ * sizeof(T),
                                          stream_);
        if (err != cudaSuccess) {
            throw std::runtime_error(std::string("cudaMallocAsync error: ") + 
                                     cudaGetErrorString(err));
        }
    }
    ~AsyncDeviceMemory() noexcept {
        if (ptr_) {
            cudaFreeAsync(ptr_, stream_);
        }
    }
    AsyncDeviceMemory(const AsyncDeviceMemory&) = delete;
    AsyncDeviceMemory& operator=(const AsyncDeviceMemory&) = delete;
    AsyncDeviceMemory(AsyncDeviceMemory&& other) noexcept 
        : ptr_(other.ptr_), count_(other.count_), stream_(other.stream_) {
        other.ptr_ = nullptr;
        other.count_ = 0;
    }
    AsyncDeviceMemory& operator=(AsyncDeviceMemory&& other) noexcept {
        if (this != &other) {
            if (ptr_) cudaFreeAsync(ptr_, stream_);
            ptr_ = other.ptr_;
            count_ = other.count_;
            stream_ = other.stream_;
            other.ptr_ = nullptr;
            other.count_ = 0;
        }
        return *this;
    }

    [[nodiscard]] T* get() noexcept { return ptr_; }
    [[nodiscard]] size_t size() const noexcept { return count_; }
    [[nodiscard]] size_t bytes() const noexcept { return count_ * sizeof(T); }

private:
    T *ptr_{nullptr};
    size_t count_{0};
    cudaStream_t stream_{nullptr};
};
