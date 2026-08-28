// telemetry.hpp
#pragma once

struct TelemetryConfig {
    uint32_t sample_rate_ms;
    bool enable_network_dump;
    constexpr TelemetryConfig(uint32_t rate, bool dump) 
        : sample_rate_ms(rate), enable_network_dump(dump) {}
};

// Єдиний екземпляр на всю програму з константною ініціалізацією:
inline constinit TelemetryConfig g_telemetry_config{100, true};
