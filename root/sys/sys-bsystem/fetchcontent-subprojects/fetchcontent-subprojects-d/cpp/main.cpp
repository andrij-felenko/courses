// src/main.cpp
#include "collector.hpp"
#include <iostream>

int main() {
    TelemetryRecord sample{
        .sensor_id = "ENV-PROBE-04",
        .temperature = 23.85,
        .pressure_hpa = 1013,
        .timestamp_ms = 1724000000000ULL
    };

    std::cout << "--- Текстовий звіт ---\n";
    std::cout << format_telemetry_report(sample) << "\n\n";

    std::cout << "--- JSON payload ---\n";
    std::cout << serialize_to_json(sample) << "\n";

    return 0;
}
