#include <cstdint>

extern "C" {
#include "lwip/opt.h"
#include "lwip/stats.h"
}

namespace embedded::diag {

inline void dumpMemoryStatistics() noexcept {
#if LWIP_STATS
    stats_display();
#endif
}

} // namespace embedded::diag
