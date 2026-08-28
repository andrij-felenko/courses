#include <stdio.h>
#include <stdlib.h>
#include <cuda_runtime.h>

#define CHUNK_SIZE (1024 * 1024)   /* 1M елементів на порцію (4 МБ) */
#define NUM_CHUNKS 8               /* Кількість порцій */
#define NUM_STREAMS 2              /* Подвійна буферизація: 2 потоки */

/* Макрос для обробки помилок CUDA API */
#define CUDA_CHECK(call) do { \
    cudaError_t err = (call); \
    if (err != cudaSuccess) { \
        fprintf(stderr, "CUDA помилка %s:%d: %s\n", \
                __FILE__, __LINE__, cudaGetErrorString(err)); \
        exit(EXIT_FAILURE); \
    } \
} while (0)

/* Обчислювальне ядро: зважене масштабування масиву */
__global__ void process_kernel(const float *in, float *out, float scale, int n) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;
    if (idx < n) {
        float val = in[idx];
        /* Інтенсивне обчислювальне навантаження для демонстрації перекриття */
        #pragma unroll
        for (int i = 0; i < 64; ++i) {
            val = val * scale + 0.001f;
        }
        out[idx] = val;
    }
}

int main(void) {
    size_t total_elements = (size_t)CHUNK_SIZE * NUM_CHUNKS;
    size_t chunk_bytes = (size_t)CHUNK_SIZE * sizeof(float);
    size_t total_bytes = total_elements * sizeof(float);

    /* 1. Виділення фіксованої (Pinned) пам'яті на хості */
    float *h_in = NULL;
    float *h_out = NULL;
    CUDA_CHECK(cudaHostAlloc((void **)&h_in, total_bytes, cudaHostAllocDefault));
    CUDA_CHECK(cudaHostAlloc((void **)&h_out, total_bytes, cudaHostAllocDefault));

    /* Ініціалізація вхідних даних */
    for (size_t i = 0; i < total_elements; ++i) {
        h_in[i] = (float)(i % 100) * 0.01f;
    }

    /* 2. Виділення подвійних буферів на пристрої (по одному на потік) */
    float *d_in[NUM_STREAMS];
    float *d_out[NUM_STREAMS];
    for (int s = 0; s < NUM_STREAMS; ++s) {
        CUDA_CHECK(cudaMalloc((void **)&d_in[s], chunk_bytes));
        CUDA_CHECK(cudaMalloc((void **)&d_out[s], chunk_bytes));
    }

    /* 3. Створення неблокуючих потоків CUDA */
    cudaStream_t streams[NUM_STREAMS];
    for (int s = 0; s < NUM_STREAMS; ++s) {
        CUDA_CHECK(cudaStreamCreateWithFlags(&streams[s], cudaStreamNonBlocking));
    }

    /* Створення подій для точного апаратного профілювання */
    cudaEvent_t start_evt, stop_evt;
    CUDA_CHECK(cudaEventCreate(&start_evt));
    CUDA_CHECK(cudaEventCreate(&stop_evt));

    dim3 block(256);
    dim3 grid((CHUNK_SIZE + block.x - 1) / block.x);

    CUDA_CHECK(cudaEventRecord(start_evt, 0));

    /* 4. Головний конвеєрний цикл */
    for (int i = 0; i < NUM_CHUNKS; ++i) {
        int stream_idx = i % NUM_STREAMS;
        size_t offset = (size_t)i * CHUNK_SIZE;

        /* Асинхронне копіювання вхідної порції: Host -> Device */
        CUDA_CHECK(cudaMemcpyAsync(d_in[stream_idx],
                                   h_in + offset,
                                   chunk_bytes,
                                   cudaMemcpyHostToDevice,
                                   streams[stream_idx]));

        /* Запуск обчислювального ядра в тому самому потоці */
        process_kernel<<<grid, block, 0, streams[stream_idx]>>>(
            d_in[stream_idx], d_out[stream_idx], 1.002f, CHUNK_SIZE
        );

        /* Асинхронне копіювання результатів: Device -> Host */
        CUDA_CHECK(cudaMemcpyAsync(h_out + offset,
                                   d_out[stream_idx],
                                   chunk_bytes,
                                   cudaMemcpyDeviceToHost,
                                   streams[stream_idx]));
    }

    /* 5. Очікування завершення всіх операцій в усіх потоках */
    for (int s = 0; s < NUM_STREAMS; ++s) {
        CUDA_CHECK(cudaStreamSynchronize(streams[s]));
    }

    CUDA_CHECK(cudaEventRecord(stop_evt, 0));
    CUDA_CHECK(cudaEventSynchronize(stop_evt));

    float elapsed_ms = 0.0f;
    CUDA_CHECK(cudaEventElapsedTime(&elapsed_ms, start_evt, stop_evt));
    printf("Конвеєрна обробка %d МБ завершена за %.2f мс\n",
           (int)(total_bytes / (1024 * 1024)), elapsed_ms);

    /* 6. Звільнення ресурсів */
    for (int s = 0; s < NUM_STREAMS; ++s) {
        CUDA_CHECK(cudaStreamDestroy(streams[s]));
        CUDA_CHECK(cudaFree(d_in[s]));
        CUDA_CHECK(cudaFree(d_out[s]));
    }
    CUDA_CHECK(cudaEventDestroy(start_evt));
    CUDA_CHECK(cudaEventDestroy(stop_evt));
    CUDA_CHECK(cudaFreeHost(h_in));
    CUDA_CHECK(cudaFreeHost(h_out));

    return 0;
}
