#pragma once

#include <chrono>
#include <cstddef>
#include <expected>
#include <span>
#include <string_view>

#include "preflight.hpp"

// Відмова, надіслана серверу кампанії: код причини, вікно повтору
// й самі виміри, щоб сервер не гадав, а планував наступний крок.

namespace ota {

enum class TelemetryCode : std::uint8_t {
    RetryCold       = 0x21,
    RetryHot        = 0x22,
    RetryLowSoc     = 0x23,
    AlertHighEsr    = 0x41,
    AlertSensorFail = 0x42,
    AlertPowerFault = 0x43
};

struct DenialReport {
    TelemetryCode        code;
    std::chrono::seconds retryAfter;      // нуль — повторювати немає сенсу
    bool                 serviceRequired; // заводити задачу технікові
};

enum class EncodeError : std::uint8_t { BufferTooSmall };

[[nodiscard]] DenialReport summarize(const Denial& denial,
                                     const SafetyLimits& limits = {}) noexcept;

[[nodiscard]] std::expected<std::span<const std::byte>, EncodeError>
encode(const Denial& denial, const SafetyLimits& limits,
       std::span<std::byte> out) noexcept;

[[nodiscard]] std::string_view name(TelemetryCode code) noexcept;
[[nodiscard]] std::string_view name(DenyReason reason) noexcept;

}  // namespace ota
