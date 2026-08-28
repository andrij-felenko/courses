// src/collector.hpp
#pragma once
#include <string>
#include <string_view>
#include <cstdint>

struct TelemetryRecord {
    std::string sensor_id;
    double temperature;
    uint32_t pressure_hpa;
    uint64_t timestamp_ms;
};

std::string format_telemetry_report(const TelemetryRecord& rec);
std::string serialize_to_json(const TelemetryRecord& rec);
