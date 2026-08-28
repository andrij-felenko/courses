#include "telemetry/metrics.h"
#include <chrono>
#include <format>
#include <string_view>
#include <cstring>

namespace {
    const auto g_start_time = std::chrono::steady_clock::now();
}

extern "C" int telemetry_collect_metrics(telemetry_snapshot_t* out_snapshot) {
    if (!out_snapshot) {
        return -1;
    }

    const auto now = std::chrono::steady_clock::now();
    const auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(now - g_start_time).count();

    out_snapshot->uptime_seconds = static_cast<uint64_t>(elapsed);
    out_snapshot->memory_used_bytes = 1048576ULL * 42ULL;
    out_snapshot->cpu_load_percent = 12.5;

    return 0;
}

extern "C" void telemetry_format_json(const telemetry_snapshot_t* snapshot, char* buffer, size_t max_len) {
    if (!snapshot || !buffer || max_len == 0) {
        return;
    }
    const std::string json = std::format(
        "{{\"uptime\": {}, \"memory_bytes\": {}, \"cpu_load\": {:.2f}}}\n",
        snapshot->uptime_seconds,
        snapshot->memory_used_bytes,
        snapshot->cpu_load_percent
    );
    const size_t copy_len = (json.size() < max_len - 1) ? json.size() : max_len - 1;
    std::memcpy(buffer, json.data(), copy_len);
    buffer[copy_len] = '\0';
}
