#include <iostream>
#include <vector>
#include <memory>
#include <stdexcept>
#include <cuda_runtime.h>

constexpr size_t N = 16 * 1024 * 1024; // 16M елементів = 64 МБ

// Користувацький видаляч для керування фіксованою пам'яттю через RAII
template <typename T>
struct CudaHostDeleter {
    void operator()(T* ptr) const noexcept {
        if (ptr) {
            cudaFreeHost(ptr);
        }
    }
};

template <typename T>
using UniquePinnedHost = std::unique_ptr<T[], CudaHostDeleter<T>>;

template <typename T>
UniquePinnedHost<T> make_pinned_buffer(size_t count) {
    void* raw_ptr = nullptr;
    cudaError_t err = cudaHostAlloc(&raw_ptr, count * sizeof(T), cudaHostAllocDefault);
    if (err != cudaSuccess) {
        throw std::runtime_error(std::string("Не вдалося виділити Pinned пам'ять: ") + 
                                 cudaGetErrorString(err));
    }
    return UniquePinnedHost<T>(static_cast<T*>(raw_ptr));
}

int main() {
    try {
        const size_t bytes = N * sizeof(float);

        // 1. Звичайна пам'ять у RAII-векторі (Pageable)
        std::vector<float> pageable_buf(N);

        // 2. Фіксована пам'ять через розумний вказівник (Pinned)
        auto pinned_buf = make_pinned_buffer<float>(N);

        // 3. Пам'ять пристрою
        float* d_data = nullptr;
        if (cudaMalloc(&d_data, bytes) != cudaSuccess) {
            throw std::runtime_error("Помилка cudaMalloc");
        }

        // Прямий DMA-трансфер з Pinned пам'яті
        if (cudaMemcpy(d_data, pinned_buf.get(), bytes, cudaMemcpyHostToDevice) != cudaSuccess) {
            cudaFree(d_data);
            throw std::runtime_error("Помилка копіювання");
        }

        cudaFree(d_data);
        std::cout << "Трансфер фіксованої пам'яті успішно виконано.\n";

    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
