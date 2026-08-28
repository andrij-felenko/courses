/* C++ RAII-обгортка для подій CUDA */
#include <cuda_runtime.h>
#include <stdexcept>

class CudaEvent {
public:
    explicit CudaEvent(unsigned int flags = cudaEventDisableTiming) {
        if (cudaEventCreateWithFlags(&event_, flags) != cudaSuccess) {
            throw std::runtime_error("cudaEventCreate failed");
        }
    }
    ~CudaEvent() noexcept {
        if (event_) cudaEventDestroy(event_);
    }
    void record(cudaStream_t stream) {
        cudaEventRecord(event_, stream);
    }
    void wait_in_stream(cudaStream_t stream) {
        cudaStreamWaitEvent(stream, event_, 0);
    }
    [[nodiscard]] cudaEvent_t get() const noexcept { return event_; }

private:
    cudaEvent_t event_{nullptr};
};
