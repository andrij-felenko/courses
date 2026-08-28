#include <stdio.h>
#include <stdlib.h>
#include <cuda_runtime.h>

#define N (16 * 1024 * 1024) /* 16M елементів = 64 МБ */

int main(void) {
    size_t bytes = N * sizeof(float);

    /* 1. Звичайна сторінкова пам'ять (повільно, подвійне копіювання) */
    float *h_pageable = (float *)malloc(bytes);

    /* 2. Фіксована пам'ять (швидко, прямий DMA-коридор) */
    float *h_pinned = NULL;
    cudaError_t err = cudaHostAlloc((void **)&h_pinned, bytes, cudaHostAllocDefault);
    if (err != cudaSuccess) {
        fprintf(stderr, "Помилка cudaHostAlloc: %s\n", cudaGetErrorString(err));
        free(h_pageable);
        return 1;
    }

    /* 3. Пам'ять пристрою у VRAM */
    float *d_data = NULL;
    cudaMalloc((void **)&d_data, bytes);

    /* Копіювання з Pinned пам'яті відбувається в 2-3 рази швидше */
    cudaMemcpy(d_data, h_pinned, bytes, cudaMemcpyHostToDevice);

    /* Звільнення ресурсів */
    cudaFree(d_data);
    cudaFreeHost(h_pinned);
    free(h_pageable);
    return 0;
}
