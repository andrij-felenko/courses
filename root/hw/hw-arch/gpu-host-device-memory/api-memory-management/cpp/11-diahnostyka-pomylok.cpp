/* C++: функція верифікації стану пристрою */
#include <cuda_runtime.h>
#include <stdexcept>
#include <string>

inline void verify_device_health() {
    cudaError_t err = cudaGetLastError();
    if (err != cudaSuccess) {
        throw std::runtime_error(std::string("GPU Health Failure: ") + 
                                 cudaGetErrorName(err) + " - " + 
                                 cudaGetErrorString(err));
    }
}
