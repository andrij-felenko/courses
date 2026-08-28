// early_pin_guard.hpp
#pragma once

#include <cstdint>
#include <span>
#include <expected>
#include <concepts>
#include <array>

namespace SystemSafety {

enum class GuardStatus : uint32_t {
    Ok = 0,
    MissingPullDown,
    MissingPullUp,
    ShortToGnd,
    ShortToVdd,
    PinBridged,
    LockFailed,
    ClockGatingFault
};

enum class HardwareLineExpectation : uint8_t {
    Floating,
    HardPullDown,
    HardPullUp
};

enum class TargetState : uint8_t {
    Input,
    OutputInactiveLow,
    OutputActiveHigh
};

struct PinConfig {
    uintptr_t port_base;
    uint8_t pin_index;
    HardwareLineExpectation expected_hardware;
    TargetState target_state;
    bool lock_configuration;
};

struct DiagnosticReport {
    std::size_t verified_count;
    std::size_t faulty_index;
    GuardStatus status;
};

// Концепт валідації списку конфігурацій пінів
template <typename T>
concept ValidPinConfigurationArray = requires(T arr) {
    { arr.size() } -> std::convertible_to<std::size_t>;
};

class PinIntegrityGuard {
public:
    template <std::size_t N>
    [[nodiscard]] static constexpr auto verify_and_arm(const std::array<PinConfig, N>& configs) noexcept
        -> std::expected<DiagnosticReport, DiagnosticReport>;

    [[nodiscard]] static bool verify_port_bridging(uintptr_t port_base, uint16_t pin_mask) noexcept;

    static void execute_emergency_shutdown(const DiagnosticReport& report) noexcept;
};

} // namespace SystemSafety
