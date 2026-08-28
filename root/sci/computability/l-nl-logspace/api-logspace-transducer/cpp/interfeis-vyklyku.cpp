// C++20 implementation: Memory usage reader with std::optional
#include <sys/resource.h>
#include <iostream>
#include <optional>
#include <cstdint>

namespace space_complexity {

[[nodiscard]] inline std::optional<uint64_t> get_peak_rss_kb() noexcept {
    struct rusage usage;
    if (getrusage(RUSAGE_SELF, &usage) == 0) {
        return static_cast<uint64_t>(usage.ru_maxrss);
    }
    return std::nullopt;
}

inline void print_peak_memory_usage() {
    if (auto rss = get_peak_rss_kb(); rss.has_value()) {
        std::cout << "Peak Resident Set Size (RSS): " << *rss << " KB\n";
    }
}

} // namespace space_complexity
