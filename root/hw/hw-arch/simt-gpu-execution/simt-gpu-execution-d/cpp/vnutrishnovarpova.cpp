// Редукція всередині варпу без Shared Memory (C++)
#include <cuda_runtime.h>

__inline__ __device__ float warp_reduce(float val)
{
    constexpr unsigned int mask = 0xffffffffU;
    // Обмін значеннями регістрів безпосередньо через комутаційну матрицю
    val += __shfl_down_sync(mask, val, 16);
    val += __shfl_down_sync(mask, val, 8);
    val += __shfl_down_sync(mask, val, 4);
    val += __shfl_down_sync(mask, val, 2);
    val += __shfl_down_sync(mask, val, 1);
    return val; // Потік 0 містить суму всіх 32 потоків
}
