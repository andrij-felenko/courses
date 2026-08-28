// C++20 procfs Memory Monitor Specification
#include <fstream>
#include <cstdint>
#include <optional>
#include <string>

namespace space_complexity {

struct ProcMemoryStats {
    uint64_t total_pages{0};
    uint64_t resident_pages{0};
    uint64_t shared_pages{0};

    [[nodiscard]] uint64_t resident_bytes(uint64_t page_size = 4096) const noexcept {
        return resident_pages * page_size;
    }
};

class ProcfsMonitor {
public:
    [[nodiscard]] static std::optional<ProcMemoryStats> current_usage() noexcept {
        std::ifstream statm_file("/proc/self/statm");
        if (!statm_file.is_open()) {
            return std::nullopt;
        }

        ProcMemoryStats stats;
        if (statm_file >> stats.total_pages >> stats.resident_pages >> stats.shared_pages) {
            return stats;
        }
        return std::nullopt;
    }
};

} // namespace space_complexity
