// warp_primitives.c (C API / CUDA C)
#include <cuda_runtime.h>

// Швидка редукція суми всередині варпу
__device__ inline float warp_reduce_sum(float val)
{
    unsigned int mask = 0xFFFFFFFF; // Усі 32 потоки активні

    // Деревна редукція: 16 -> 8 -> 4 -> 2 -> 1
    val += __shfl_down_sync(mask, val, 16);
    val += __shfl_down_sync(mask, val, 8);
    val += __shfl_down_sync(mask, val, 4);
    val += __shfl_down_sync(mask, val, 2);
    val += __shfl_down_sync(mask, val, 1);

    // Потік 0 містить фінальну суму всіх 32 потоків
    return val;
}

// Префіксне сумування (Inclusive Scan) всередині варпу
__device__ inline float warp_prefix_scan(float val)
{
    unsigned int mask = 0xFFFFFFFF;

    for (int offset = 1; offset < 32; offset <<= 1) {
        float temp = __shfl_up_sync(mask, val, offset);
        if ((threadIdx.x & 31) >= offset) {
            val += temp;
        }
    }
    return val;
}
