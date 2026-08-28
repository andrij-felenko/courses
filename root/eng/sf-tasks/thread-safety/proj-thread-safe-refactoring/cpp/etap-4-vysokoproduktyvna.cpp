#include <cstdint>

namespace fast_metrics {

struct LocalCounters {
    uint64_t total_bytes{0};
    uint64_t error_count{0};
};

// Кожен потік володіє незалежним екземпляром структури
inline thread_local LocalCounters tls_counters{};

void record(int status_code, uint64_t bytes) noexcept {
    tls_counters.total_bytes += bytes;
    if (status_code >= 400) {
        ++tls_counters.error_count;
    }
}

[[nodiscard]] LocalCounters get_local() noexcept {
    return tls_counters;
}

} // namespace fast_metrics
