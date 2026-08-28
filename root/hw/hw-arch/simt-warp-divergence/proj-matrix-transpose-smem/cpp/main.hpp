// matrix_transpose.cuh (Modern CUDA C++20 / Templates / RAII)
#pragma once
#include <cuda_runtime.h>
#include <iostream>
#include <memory>
#include <span>
#include <stdexcept>

namespace gpu {

// RAII обгортка для керування пам'яттю GPU
template <typename T>
class DeviceBuffer {
public:
    explicit DeviceBuffer(std::size_t count) : count_(count) {
        cudaError_t err = cudaMalloc(&ptr_, count_ * sizeof(T));
        if (err != cudaSuccess) {
            throw std::runtime_error(cudaGetErrorString(err));
        }
    }

    ~DeviceBuffer() noexcept {
        if (ptr_) {
            cudaFree(ptr_);
        }
    }

    DeviceBuffer(const DeviceBuffer &) = delete;
    DeviceBuffer &operator=(const DeviceBuffer &) = delete;

    DeviceBuffer(DeviceBuffer &&other) noexcept : ptr_(other.ptr_), count_(other.count_) {
        other.ptr_ = nullptr;
        other.count_ = 0;
    }

    DeviceBuffer &operator=(DeviceBuffer &&other) noexcept {
        if (this != &other) {
            if (ptr_) cudaFree(ptr_);
            ptr_ = other.ptr_;
            count_ = other.count_;
            other.ptr_ = nullptr;
            other.count_ = 0;
        }
        return *this;
    }

    [[nodiscard]] T *data() noexcept { return ptr_; }
    [[nodiscard]] const T *data() const noexcept { return ptr_; }
    [[nodiscard]] std::size_t size() const noexcept { return count_; }

private:
    T *ptr_{nullptr};
    std::size_t count_{0};
};

// Конфігурація плитки
template <int TileDim = 32, int BlockRows = 8>
struct TransposeConfig {
    static constexpr int tile_dim = TileDim;
    static constexpr int block_rows = BlockRows;
};

// Шаблонне ядро транспонування з вибором стратегії уникнення банківських конфліктів
enum class ConflictStrategy {
    None,     // 32-кратний конфлікт
    Padding,  // Паддинг рядків
    Swizzle   // XOR перестановка індексів
};

template <ConflictStrategy Strategy, int TileDim = 32, int BlockRows = 8>
__global__ void transpose_kernel(float * __restrict__ out, const float * __restrict__ in, int width, int height)
{
    // Статичний вибір розкладки пам'яті на етапі компіляції
    constexpr int pad_cols = (Strategy == ConflictStrategy::Padding) ? (TileDim + 1) : TileDim;
    __shared__ float tile[TileDim][pad_cols];

    int x = blockIdx.x * TileDim + threadIdx.x;
    int y = blockIdx.y * TileDim + threadIdx.y;

    #pragma unroll
    for (int j = 0; j < TileDim; j += BlockRows) {
        if ((y + j) < height && x < width) {
            int row = threadIdx.y + j;
            int col = threadIdx.x;
            if constexpr (Strategy == ConflictStrategy::Swizzle) {
                tile[row][col ^ (row & (TileDim - 1))] = in[(y + j) * width + x];
            } else {
                tile[row][col] = in[(y + j) * width + x];
            }
        }
    }

    __syncthreads();

    x = blockIdx.y * TileDim + threadIdx.x;
    y = blockIdx.x * TileDim + threadIdx.y;

    #pragma unroll
    for (int j = 0; j < TileDim; j += BlockRows) {
        if ((y + j) < width && x < height) {
            int row = threadIdx.x;
            int col = threadIdx.y + j;
            if constexpr (Strategy == ConflictStrategy::Swizzle) {
                out[(y + j) * height + x] = tile[row][col ^ (row & (TileDim - 1))];
            } else {
                out[(y + j) * height + x] = tile[row][col];
            }
        }
    }
}

} // namespace gpu
