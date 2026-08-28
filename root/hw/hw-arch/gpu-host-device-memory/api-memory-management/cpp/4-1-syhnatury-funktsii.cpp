/* C++ інтерфейс типізованого виділення фіксованого буфера */
#include <cuda_runtime.h>
#include <span>
#include <memory>
#include <new>

template <typename T>
struct PinnedDeleter {
    void operator()(T *ptr) const noexcept {
        if (ptr) cudaFreeHost(ptr);
    }
};

template <typename T>
using UniquePinned = std::unique_ptr<T[], PinnedDeleter<T>>;

template <typename T>
UniquePinned<T> make_pinned(size_t count, unsigned int flags = cudaHostAllocDefault) {
    void *raw = nullptr;
    cudaError_t err = cudaHostAlloc(&raw, count * sizeof(T), flags);
    if (err != cudaSuccess) {
        throw std::bad_alloc();
    }
    return UniquePinned<T>(static_cast<T*>(raw));
}
