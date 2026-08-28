// src/telemetry_consumer.hpp
#pragma once
#include <cstdint>
#include <span>
#include <string_view>

namespace telemetry {
    struct Record {
        std::uint64_t timestamp_ns{0};
        std::uint32_t sensor_id{0};
        double metric_value{0.0};
    };

    [[nodiscard]] bool dispatch_records(std::span<const Record> batch) noexcept;
}
