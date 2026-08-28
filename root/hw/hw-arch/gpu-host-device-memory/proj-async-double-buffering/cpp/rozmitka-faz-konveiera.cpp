/* C++: RAII-обгортка діапазону NVTX */
#include <nvtx3/nvToolsExt.h>

class NvtxScope {
public:
    explicit NvtxScope(const char* name) {
        nvtxRangePushA(name);
    }
    ~NvtxScope() noexcept {
        nvtxRangePop();
    }
    NvtxScope(const NvtxScope&) = delete;
    NvtxScope& operator=(const NvtxScope&) = delete;
};
