#include <iostream>
#include <chrono>
#include <optional>
#include <malloc.h>
#include <cstdint>
#include <string_view>
#include <format>

struct MemoryTelemetry {
    uint64_t timestamp_ms{0};
    std::size_t total_free_bytes{0};
    std::size_t max_contiguous_free_bytes{0};
    double fragmentation_index{0.0};
    uint32_t max_isr_latency_us{0};
};

class SystemProbe {
public:
    static MemoryTelemetry capture(uint32_t isr_latency_us) noexcept {
        MemoryTelemetry report;
        const auto now = std::chrono::steady_clock::now().time_since_epoch();
        report.timestamp_ms = std::chrono::duration_cast<std::chrono::milliseconds>(now).count();

        const struct mallinfo2 info = mallinfo2();
        report.total_free_bytes = static_cast<std::size_t>(info.fordblks);
        report.max_contiguous_free_bytes = probe_max_block(report.total_free_bytes);

        if (report.total_free_bytes > 0) {
            report.fragmentation_index = 1.0 - (static_cast<double>(report.max_contiguous_free_bytes) /
                                                static_cast<double>(report.total_free_bytes));
        } else {
            report.fragmentation_index = 1.0;
        }

        report.max_isr_latency_us = isr_latency_us;
        return report;
    }

    static void emit_json(const MemoryTelemetry& rep) {
        std::cout << "{\"type\":\"soak_telemetry\","
                  << "\"ts\":" << rep.timestamp_ms << ","
                  << "\"free_bytes\":" << rep.total_free_bytes << ","
                  << "\"max_block\":" << rep.max_contiguous_free_bytes << ","
                  << "\"frag_idx\":" << rep.fragmentation_index << ","
                  << "\"max_latency_us\":" << rep.max_isr_latency_us << "}\n"
                  << std::flush;
    }

private:
    static std::size_t probe_max_block(std::size_t upper_bound) noexcept {
        std::size_t low = 0;
        std::size_t high = upper_bound;
        std::size_t max_success = 0;

        while (low <= high) {
            const std::size_t mid = low + (high - low) / 2;
            if (mid == 0) {
                low = 1;
                continue;
            }

            void* ptr = ::malloc(mid);
            if (ptr != nullptr) {
                max_success = mid;
                ::free(ptr);
                low = mid + 1;
            } else {
                if (mid == 0) break;
                high = mid - 1;
            }
        }
        return max_success;
    }
};
