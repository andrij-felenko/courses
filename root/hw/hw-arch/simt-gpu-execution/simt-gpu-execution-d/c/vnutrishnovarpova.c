// Редукція всередині варпу без Shared Memory (C)
__inline__ __device__ float warp_reduce(float val)
{
    // Обмін значеннями регістрів безпосередньо через комутаційну матрицю
    val += __shfl_down_sync(0xffffffff, val, 16);
    val += __shfl_down_sync(0xffffffff, val, 8);
    val += __shfl_down_sync(0xffffffff, val, 4);
    val += __shfl_down_sync(0xffffffff, val, 2);
    val += __shfl_down_sync(0xffffffff, val, 1);
    return val; // Потік 0 містить суму всіх 32 потоків
}
