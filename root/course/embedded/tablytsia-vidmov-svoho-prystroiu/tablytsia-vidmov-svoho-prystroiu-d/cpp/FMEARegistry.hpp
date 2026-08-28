// FMEARegistry.hpp / FMEARegistry.cpp — Типобезпечний реєстр відмов на C++20
#pragma once

#include <cstdint>
#include <string_view>
#include <span>
#include <array>
#include <functional>

namespace embedded::fmea {

enum class ActionPriority : uint8_t {
    Low = 0,
    Medium,
    High
};

enum class FailureId : uint8_t {
    PowerSupply = 0,
    ValveMosfet,
    PressureSensor,
    I2cBus,
    FlashMemory,
    StackOverflow,
    Count
};

struct Record {
    FailureId           id;
    std::string_view    name;
    uint8_t             severity;
    uint8_t             occurrence;
    uint8_t             detection;
    ActionPriority      ap;
    bool (*diag_func)() = nullptr;
    void (*recovery_func)() = nullptr;

    [[nodiscard]] constexpr uint16_t rpn() const noexcept {
        return static_cast<uint16_t>(severity * occurrence * detection);
    }
};

struct RuntimeState {
    uint32_t fail_count{0};
    uint32_t last_fail_timestamp_ms{0};
    bool     is_active{false};
};

[[nodiscard]] constexpr ActionPriority calculate_ap(uint8_t s, uint8_t o, uint8_t d) noexcept {
    if (s >= 9) {
        if (o >= 2) return ActionPriority::High;
        return (d >= 5) ? ActionPriority::High : ActionPriority::Medium;
    }
    if (s >= 7) {
        if (o >= 8) return ActionPriority::High;
        if (o >= 6) return (d >= 5) ? ActionPriority::High : ActionPriority::Medium;
        if (o >= 4) return (d >= 7) ? ActionPriority::High : ActionPriority::Medium;
        return (d >= 7) ? ActionPriority::Medium : ActionPriority::Low;
    }
    if (s >= 4) {
        if (o >= 8) return (d >= 7) ? ActionPriority::High : ActionPriority::Medium;
        if (o >= 6) return ActionPriority::Medium;
        return (d >= 7) ? ActionPriority::Medium : ActionPriority::Low;
    }
    return (o >= 8 && d >= 7) ? ActionPriority::Medium : ActionPriority::Low;
}

class Supervisor {
public:
    static constexpr size_t RecordCount = static_cast<size_t>(FailureId::Count);

    Supervisor(std::span<const Record, RecordCount> registry) noexcept
        : m_registry(registry) {}

    void run_diagnostics(uint32_t current_time_ms) noexcept {
        for (size_t i = 0; i < RecordCount; ++i) {
            const auto& rec = m_registry[i];
            if (!rec.diag_func) continue;

            if (!rec.diag_func()) {
                m_state[i].fail_count++;
                m_state[i].last_fail_timestamp_ms = current_time_ms;
                m_state[i].is_active = true;

                if (rec.recovery_func) {
                    rec.recovery_func();
                }
            } else {
                m_state[i].is_active = false;
            }
        }
    }

    [[nodiscard]] bool is_system_safe() const noexcept {
        for (size_t i = 0; i < RecordCount; ++i) {
            if (m_state[i].is_active && m_registry[i].severity >= 8) {
                return false;
            }
        }
        return true;
    }

    [[nodiscard]] const RuntimeState& get_state(FailureId id) const noexcept {
        return m_state[static_cast<size_t>(id)];
    }

private:
    std::span<const Record, RecordCount> m_registry;
    std::array<RuntimeState, RecordCount> m_state{};
};

} // namespace embedded::fmea
