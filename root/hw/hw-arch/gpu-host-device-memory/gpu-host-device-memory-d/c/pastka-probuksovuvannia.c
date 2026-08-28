/* C: використання керованої пам'яті з завчасним префетчингом */
#include <cuda_runtime.h>

void run_managed_computation(size_t bytes, size_t n, int device_id, cudaStream_t stream) {
    float *data = NULL;
    cudaMallocManaged((void **)&data, bytes, cudaMemAttachGlobal);

    /* Ініціалізація на CPU */
    for (size_t i = 0; i < n; ++i) data[i] = 1.0f;

    /* Завчасне підтягування сторінок у VRAM перед стартом ядра */
    cudaMemPrefetchAsync(data, bytes, device_id, stream);

    /* Ядро стартує без жодного Page Fault */
    /* kernel<<<grid, block, 0, stream>>>(data, n); */

    /* Повернення сторінок у системну RAM */
    cudaMemPrefetchAsync(data, bytes, cudaCpuDeviceId, stream);
    cudaStreamSynchronize(stream);

    cudaFree(data);
}
