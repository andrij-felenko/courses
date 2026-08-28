/* C++ RAII-обгортка з контролем винятків */
#include <cuda_runtime.h>
#include <stdexcept>
#include <string>

template <typename T>
class DeviceMemory {
public:
    explicit DeviceMemory(size_t count) : count_(count) {
        cudaError_t err = cudaMalloc(reinterpret_cast<void**>(&ptr_), count_ * sizeof(T));
        if (err != cudaSuccess) {
            throw std::runtime_error(std::string("cudaMalloc error: ") + cudaGetErrorString(err));
        }
    }
    ~DeviceMemory() noexcept {
        if (ptr_) {
            cudaFree(ptr_);
        }
    }
    DeviceMemory(const DeviceMemory&) = delete;
    DeviceMemory& operator=(const DeviceMemory&) = delete;
    DeviceMemory(DeviceMemory&& other) noexcept : ptr_(other.ptr_), count_(other.count_) {
        other.ptr_ = nullptr;
        other.count_ = 0;
    }
    DeviceMemory& operator=(DeviceMemory&& other) noexcept {
        if (this != &other) {
            if (ptr_) cudaFree(ptr_);
            ptr_ = other.ptr_;
            count_ = other.count_;
            other.ptr_ = nullptr;
            other.count_ = 0;
        }
        return *this;
    }

    [[nodiscard]] T* get() noexcept { return ptr_; }
    [[nodiscard]] const T* get() const noexcept { return ptr_; }
    [[nodiscard]] size_t size() const noexcept { return count_; }
    [[nodiscard]] size_t bytes() const noexcept { return count_ * sizeof(T); }

private:
    T *ptr_{nullptr};
    size_t count_{0};
};
