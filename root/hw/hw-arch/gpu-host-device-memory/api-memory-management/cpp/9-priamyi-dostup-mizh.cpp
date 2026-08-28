/* C++ утиліта підключення прямого P2P доступу між двома картами */
#include <cuda_runtime.h>
#include <iostream>

inline bool enable_p2p_if_supported(int dev_a, int dev_b) {
    int can_access = 0;
    cudaDeviceCanAccessPeer(&can_access, dev_a, dev_b);
    if (can_access) {
        cudaSetDevice(dev_a);
        cudaError_t err = cudaDeviceEnablePeerAccess(dev_b, 0);
        return (err == cudaSuccess || err == cudaErrorPeerAccessAlreadyEnabled);
    }
    return false;
}
