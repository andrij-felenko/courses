#pragma once

#include <cstddef>
#include <cstdint>
#include <string>
#include <string_view>

namespace telemetry {

struct Snapshot {
    std::uint64_t uptime_seconds{0};
    std::uint64_t memory_used_bytes{0};
    double cpu_load_percent{0.0};
};

bool collect_metrics(Snapshot& out_snapshot);
std::string format_json(const Snapshot& snapshot);

} // namespace telemetry
