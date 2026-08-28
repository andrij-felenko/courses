// Ідіоматична RAII-обгортка для PD у C++20
#include <infiniband/verbs.h>
#include <memory>
#include <stdexcept>

struct IbvContextDeleter {
    void operator()(ibv_context* ctx) const noexcept {
        if (ctx) ibv_close_device(ctx);
    }
};

struct IbvPdDeleter {
    void operator()(ibv_pd* pd) const noexcept {
        if (pd) ibv_dealloc_pd(pd);
    }
};

using UniqueContext = std::unique_ptr<ibv_context, IbvContextDeleter>;
using UniquePd      = std::unique_ptr<ibv_pd, IbvPdDeleter>;

UniquePd make_protection_domain(ibv_context* ctx) {
    ibv_pd* pd = ibv_alloc_pd(ctx);
    if (!pd) {
        throw std::runtime_error("Не вдалося виділити Protection Domain");
    }
    return UniquePd(pd);
}
