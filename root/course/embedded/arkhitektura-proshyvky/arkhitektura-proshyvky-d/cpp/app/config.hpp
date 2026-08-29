// app/config.hpp — числа, що залежать від конкретного виробу.
// Усі constexpr: жодне з них не займе байта в оперативній пам'яті.
#pragma once

#include "hal/clock.hpp"

#include <cstddef>
#include <cstdint>

namespace config {

// Адреси мікросхем на шині I2C (7-бітні).
inline constexpr std::uint8_t kBme280Address  = 0x76;  // SDO на землі
inline constexpr std::uint8_t kAdxl345Address = 0x53;  // ALT ADDRESS на землі

inline constexpr std::size_t kEventQueueCapacity = 32;

inline constexpr hal::Millis kTickPeriod{100};
inline constexpr hal::Millis kTelemetryWindow{10000};

// Пороги бізнес-політики.
inline constexpr float kTempLimitC      = 65.0F;
inline constexpr float kTempHysteresisC = 3.0F;
inline constexpr float kVibrationLimitG = 2.5F;

inline constexpr std::uint32_t kSensorFaultLimit = 5;

} // namespace config
