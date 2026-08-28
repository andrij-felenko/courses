#include <cstddef>
#include <cstdint>

namespace ribbon {

struct Stats {
    std::size_t num_keys{0};
    std::size_t num_slots{0};
    std::size_t memory_bytes{0};
    double bits_per_key{0.0};
    double theoretical_fpr{0.0};
    std::uint32_t retries_count{0};
    double build_time_ms{0.0};
};

} // namespace ribbon
