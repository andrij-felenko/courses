/* telemetry_static_pool.cpp — статичний пул у C++ */
#include "telemetry_engine.hpp"
#include <array>
#include <vector>

namespace {
    constexpr size_t kMaxStaticEngines = 4;
    std::array<bool, kMaxStaticEngines> g_in_use{false};
}

class StaticTelemetryPool {
public:
    static std::unique_ptr<TelemetryEngine> acquire(const TelemetryConfig &cfg) {
        for (size_t i = 0; i < kMaxStaticEngines; ++i) {
            if (!g_in_use[i]) {
                g_in_use[i] = true;
                return std::make_unique<TelemetryEngine>(cfg);
            }
        }
        return nullptr;
    }
};
