// Обгортка створення конфігурації perf_event_attr у C++20
#include <linux/perf_event.h>
#include <cstdint>
#include <cstring>

namespace sys {
    inline perf_event_attr make_hardware_attr(std::uint64_t config, std::uint64_t sample_period) noexcept {
        perf_event_attr attr{};
        attr.type = PERF_TYPE_HARDWARE;
        attr.size = sizeof(perf_event_attr);
        attr.config = config;
        attr.sample_period = sample_period;
        attr.sample_type = PERF_SAMPLE_IP | PERF_SAMPLE_TID | PERF_SAMPLE_TIME;
        attr.disabled = 1;
        attr.exclude_kernel = 1;
        attr.exclude_hv = 1;
        return attr;
    }
}
