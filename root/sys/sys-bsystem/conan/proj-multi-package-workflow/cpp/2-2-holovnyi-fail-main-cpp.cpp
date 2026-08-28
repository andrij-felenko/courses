#include <telemetry/telemetry.hpp>
#include <fmt/core.h>
#include <nlohmann/json.hpp>

#include <iostream>
#include <vector>

int main() {
    try {
        telemetry::PacketEncoder encoder("flight_telemetry");

        std::vector<telemetry::SensorRecord> batch = {
            {.sensor_id = 1, .timestamp_ns = 1718900000100ULL, .value = 101.325},
            {.sensor_id = 2, .timestamp_ns = 1718900000200ULL, .value = 298.150},
            {.sensor_id = 3, .timestamp_ns = 1718900000300ULL, .value = 9.80665}
        };

        auto binary_blob = encoder.encode(batch);

        nlohmann::json report;
        report["channel"] = encoder.channel_name();
        report["records_count"] = batch.size();
        report["encoded_bytes"] = binary_blob.size();
        report["status"] = "OK";

        fmt::print("Телеметричний звіт:\n{}\n", report.dump(4));
        return 0;
    } catch (const std::exception& e) {
        fmt::print(stderr, "Помилка демона: {}\n", e.what());
        return 1;
    }
}
