// matrix_transpose.cu (C API / CUDA C)
#include <cuda_runtime.h>
#include <stdio.h>

#define TILE_DIM 32
#define BLOCK_ROWS 8

// 1. Ядро з 32-кратним банківським конфліктом
__global__ void transpose_naive_shared(float *out, const float *in, int width, int height)
{
    __shared__ float tile[TILE_DIM][TILE_DIM];

    int x = blockIdx.x * TILE_DIM + threadIdx.x;
    int y = blockIdx.y * TILE_DIM + threadIdx.y;

    // Коалесцентне зчитування з глобальної пам'яті
    for (int j = 0; j < TILE_DIM; j += BLOCK_ROWS) {
        if ((y + j) < height && x < width) {
            tile[threadIdx.y + j][threadIdx.x] = in[(y + j) * width + x];
        }
    }

    __syncthreads();

    // Перераховуємо координати для запису транспонованого блоку
    x = blockIdx.y * TILE_DIM + threadIdx.x;
    y = blockIdx.x * TILE_DIM + threadIdx.y;

    // 32-кратний банківський конфлікт: threadIdx.x звертається до однакових банків!
    for (int j = 0; j < TILE_DIM; j += BLOCK_ROWS) {
        if ((y + j) < width && x < height) {
            out[(y + j) * height + x] = tile[threadIdx.x][threadIdx.y + j];
        }
    }
}

// 2. Оптимізоване ядро з паддингом (+1 колонка)
__global__ void transpose_padded_shared(float *out, const float *in, int width, int height)
{
    // Паддинг [32][33] зсуває банки кожного рядка на 1
    __shared__ float tile[TILE_DIM][TILE_DIM + 1];

    int x = blockIdx.x * TILE_DIM + threadIdx.x;
    int y = blockIdx.y * TILE_DIM + threadIdx.y;

    for (int j = 0; j < TILE_DIM; j += BLOCK_ROWS) {
        if ((y + j) < height && x < width) {
            tile[threadIdx.y + j][threadIdx.x] = in[(y + j) * width + x];
        }
    }

    __syncthreads();

    x = blockIdx.y * TILE_DIM + threadIdx.x;
    y = blockIdx.x * TILE_DIM + threadIdx.y;

    // 0 банківських конфліктів: gcd(33, 32) = 1
    for (int j = 0; j < TILE_DIM; j += BLOCK_ROWS) {
        if ((y + j) < width && x < height) {
            out[(y + j) * height + x] = tile[threadIdx.x][threadIdx.y + j];
        }
    }
}

// 3. Оптимізоване ядро з XOR-свізлінгом (без перевитрати пам'яті)
__global__ void transpose_swizzled_shared(float *out, const float *in, int width, int height)
{
    __shared__ float tile[TILE_DIM][TILE_DIM];

    int x = blockIdx.x * TILE_DIM + threadIdx.x;
    int y = blockIdx.y * TILE_DIM + threadIdx.y;

    for (int j = 0; j < TILE_DIM; j += BLOCK_ROWS) {
        if ((y + j) < height && x < width) {
            int row = threadIdx.y + j;
            int col = threadIdx.x;
            tile[row][col ^ (row & 31)] = in[(y + j) * width + x];
        }
    }

    __syncthreads();

    x = blockIdx.y * TILE_DIM + threadIdx.x;
    y = blockIdx.x * TILE_DIM + threadIdx.y;

    for (int j = 0; j < TILE_DIM; j += BLOCK_ROWS) {
        if ((y + j) < width && x < height) {
            int row = threadIdx.x;
            int col = threadIdx.y + j;
            out[(y + j) * height + x] = tile[row][col ^ (row & 31)];
        }
    }
}
