#pragma once

#include <cstdint>
#include <expected>
#include <optional>
#include <string_view>

/*
 * Типи розподіленого стану вузла (C++23).
 * Дельта тіні тут — не маска бітів, а набір std::optional: поле або приїхало,
 * або ні, і компілятор не дасть прочитати те, чого хмара не надсилала.
 */
namespace iot {

inline constexpr float kMinTargetC = 5.0F;
inline constexpr float kMaxTargetC = 40.0F;
inline constexpr std::uint16_t kMaxFanRpm = 3000;
inline constexpr float kTempEpsilonC = 0.05F; /* дрібніша різниця — шум float */

struct NodeConfig {
    float targetTemperature{20.0F};
    std::uint16_t fanSpeedRpm{1000};
    bool heatingEnabled{false};
    std::uint32_t sequenceId{0}; /* монотонна версія тіні */
};

struct ConfigDelta {
    std::uint32_t sequenceId{0};
    std::optional<float> targetTemperature{};
    std::optional<std::uint16_t> fanSpeedRpm{};
    std::optional<bool> heatingEnabled{};

    [[nodiscard]] constexpr bool empty() const noexcept {
        return !targetTemperature && !fanSpeedRpm && !heatingEnabled;
    }

    [[nodiscard]] constexpr int fieldCount() const noexcept {
        return static_cast<int>(targetTemperature.has_value()) +
               static_cast<int>(fanSpeedRpm.has_value()) +
               static_cast<int>(heatingEnabled.has_value());
    }
};

enum class DeltaError : std::uint8_t {
    Stale,      /* версія не новіша за прийняту: дубль або обгін пакетів */
    Empty,      /* документ без жодного поля */
    OutOfRange  /* значення поза фізичними межами об'єкта */
};

[[nodiscard]] std::string_view describe(DeltaError error) noexcept;

/* Фізична валідація на краю. Порожній expected — усе гаразд. */
[[nodiscard]] inline std::expected<void, DeltaError> validate(const ConfigDelta& delta) noexcept
{
    if (delta.empty()) {
        return std::unexpected(DeltaError::Empty);
    }
    if (delta.targetTemperature &&
        (!(*delta.targetTemperature >= kMinTargetC) || !(*delta.targetTemperature <= kMaxTargetC))) {
        return std::unexpected(DeltaError::OutOfRange); /* заперечення ловить і NaN */
    }
    if (delta.fanSpeedRpm && (*delta.fanSpeedRpm > kMaxFanRpm)) {
        return std::unexpected(DeltaError::OutOfRange);
    }
    return {};
}

/* Різниця двох конфігурацій як дельта: що саме треба довести до заліза. */
[[nodiscard]] ConfigDelta difference(const NodeConfig& desired, const NodeConfig& active) noexcept;

} // namespace iot
