/* C++: RAII-обгортка виконуваного графа CUDA */
#include <cuda_runtime.h>
#include <stdexcept>

class CudaGraphExecutor {
public:
    explicit CudaGraphExecutor(cudaGraph_t graph) {
        if (cudaGraphInstantiate(&instance_, graph, nullptr, nullptr, 0) != cudaSuccess) {
            throw std::runtime_error("cudaGraphInstantiate failed");
        }
    }
    ~CudaGraphExecutor() noexcept {
        if (instance_) cudaGraphExecDestroy(instance_);
    }
    void launch(cudaStream_t stream) {
        cudaGraphLaunch(instance_, stream);
    }

private:
    cudaGraphExec_t instance_{nullptr};
};
