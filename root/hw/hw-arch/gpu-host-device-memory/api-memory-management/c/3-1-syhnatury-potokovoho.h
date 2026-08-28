/* CUDA Runtime API */
cudaError_t cudaMallocAsync(void **devPtr, size_t size, cudaStream_t stream);
cudaError_t cudaFreeAsync(void *devPtr, cudaStream_t stream);

cudaError_t cudaMemPoolCreate(cudaMemPool_t *memPool, const cudaMemPoolProps *poolProps);
cudaError_t cudaMemPoolDestroy(cudaMemPool_t memPool);
cudaError_t cudaMemPoolTrimTo(cudaMemPool_t memPool, size_t minBytesToKeep);

/* ROCm HIP API */
hipError_t hipMallocAsync(void **devPtr, size_t size, hipStream_t stream);
hipError_t hipFreeAsync(void *devPtr, hipStream_t stream);
