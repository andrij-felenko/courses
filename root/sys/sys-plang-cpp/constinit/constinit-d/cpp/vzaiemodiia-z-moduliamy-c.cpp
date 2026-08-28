// telemetry_system.ixx
export module telemetry_system;

import <string_view>;
import <atomic>;

export struct MetricCounter {
    std::string_view name;
    std::atomic<uint64_t> count{0};

    constexpr MetricCounter(std::string_view n) noexcept : name(n), count(0) {}
};

// Експортований глобальний лічильник із константною ініціалізацією:
export constinit MetricCounter g_active_connections{"network.active_connections"};
