/* C++ допоміжна функція отримання device покажчика */
#include <cuda_runtime.h>
#include <stdexcept>

template <typename T>
T* get_mapped_device_pointer(T* host_mapped_ptr) {
    void* dev_ptr = nullptr;
    cudaError_t err = cudaHostGetDevicePointer(&dev_ptr, host_mapped_ptr, 0);
    if (err != cudaSuccess) {
        throw std::runtime_error("cudaHostGetDevicePointer failed");
    }
    return static_cast<T*>(dev_ptr);
}
