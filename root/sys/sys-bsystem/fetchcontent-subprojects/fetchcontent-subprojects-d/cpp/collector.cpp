// src/collector.cpp
#include "collector.hpp"
#include <fmt/format.h>
#include <fmt/chrono.h>
#include <nlohmann/json.hpp>
#include <chrono>

std::string format_telemetry_report(const TelemetryRecord& rec) {
    const auto tp = std::chrono::time_point<std::chrono::system_clock, std::chrono::milliseconds>(
        std::chrono::milliseconds(rec.timestamp_ms)
    );

    // Використання форматування fmt: чисто, швидко, без ризику виходу за межі буфера
    return fmt::format("[{:%Y-%m-%d %H:%M:%S}] Sensor '{}': Temp = {:.2f} °C, Pressure = {} hPa",
                       tp, rec.sensor_id, rec.temperature, rec.pressure_hpa);
}

std::string serialize_to_json(const TelemetryRecord& rec) {
    nlohmann::json j;
    j["sensor_id"] = rec.sensor_id;
    j["metrics"] = {
        {"temperature_c", rec.temperature},
        {"pressure_hpa", rec.pressure_hpa}
    };
    j["timestamp"] = rec.timestamp_ms;
    return j.dump(2);
}
