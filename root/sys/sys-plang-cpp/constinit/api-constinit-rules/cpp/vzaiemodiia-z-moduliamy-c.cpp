// telemetry_module.ixx
export module telemetry;

export struct SessionMetrics {
    unsigned long requests_count;
    unsigned long errors_count;
    constexpr SessionMetrics() : requests_count(0), errors_count(0) {}
};

export constinit SessionMetrics g_session_metrics{};
