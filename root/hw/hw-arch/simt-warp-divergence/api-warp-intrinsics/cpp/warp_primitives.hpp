// warp_primitives.hpp (Modern CUDA C++ / Type-safe Templates)
#pragma once
#include <cuda_runtime.h>
#include <concepts>
#include <type_traits>

namespace gpu {

// Концепт арифметичного типу, що підтримується апаратним shuffle
template <typename T>
concept Shuffleable = std::is_arithmetic_v<T> && (sizeof(T) == 4 || sizeof(T) == 8);

// Універсальна типобезпечна редукція варпу
template <Shuffleable T, typename BinaryOp>
__device__ inline T warp_reduce(T val, BinaryOp op, unsigned int mask = 0xFFFFFFFF) noexcept
{
    #pragma unroll
    for (int offset = 16; offset > 0; offset >>= 1) {
        T other = __shfl_down_sync(mask, val, offset);
        val = op(val, other);
    }
    return val;
}

// Спеціалізація суми для довільного числового типу
template <Shuffleable T>
__device__ inline T warp_sum(T val, unsigned int mask = 0xFFFFFFFF) noexcept
{
    return warp_reduce(val, [](T a, T b) { return a + b; }, mask);
}

// Спеціалізація максимуму
template <Shuffleable T>
__device__ inline T warp_max(T val, unsigned int mask = 0xFFFFFFFF) noexcept
{
    return warp_reduce(val, [](T a, T b) { return (a > b) ? a : b; }, mask);
}

} // namespace gpu
