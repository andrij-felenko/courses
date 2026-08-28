// C++20: Концепт апаратної шини для типізованої ін'єкції залежностей
#pragma once
#include <cstdint>
#include <span>
#include <concepts>

namespace embedded::drivers {

enum class BusResult : std::int32_t {
    Success = 0,
    HardwareError = -1,
    Timeout = -2
};

template <typename T>
concept BusInterface = requires(T bus, std::uint8_t reg, std::span<std::uint8_t> rx, std::span<const std::uint8_t> tx) {
    { bus.read(reg, rx) } -> std::same_as<BusResult>;
    { bus.write(reg, tx) } -> std::same_as<BusResult>;
    { bus.delay_ms(std::uint32_t{}) } -> std::same_as<void>;
};

} // namespace embedded::drivers
