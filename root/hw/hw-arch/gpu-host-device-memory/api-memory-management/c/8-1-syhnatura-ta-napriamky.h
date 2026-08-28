/* CUDA Runtime API */
cudaError_t cudaMemcpyAsync(void *dst,
                            const void *src,
                            size_t count,
                            enum cudaMemcpyKind kind,
                            cudaStream_t stream);

/* ROCm HIP API */
hipError_t hipMemcpyAsync(void *dst,
                          const void *src,
                          size_t count,
                          hipMemcpyKind kind,
                          hipStream_t stream);
