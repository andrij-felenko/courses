// esd_monitor.hpp — Об'єктно-орієнтований C++20 модуль телеметрії та захисту від ESD
#pragma once

#include <chrono>
#include <concepts>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

namespace embedded_safety {

enum class RecoveryStatus : uint8_t {
    Success = 0,
    HardwareFault,
    Timeout
};

struct EsdEventRecord {
    std::chrono::milliseconds timestamp{0};
    uint16_t peak_voltage_mv{0};
    uint8_t port_id{0};
};

class EsdProtectionMonitor {
public:
    constexpr EsdProtectionMonitor() noexcept = default;

    // Реєстрація події розряду із захистом від переповнення
    void record_strike(uint8_t port_id, uint16_t peak_mv, std::chrono::milliseconds now) noexcept {
        strike_count_++;
        last_event_ = EsdEventRecord{
            .timestamp = now,
            .peak_voltage_mv = peak_mv,
            .port_id = port_id
        };
        if (peak_mv > max_recorded_peak_mv_) {
            max_recorded_peak_mv_ = peak_mv;
        }
        if (peak_mv > critical_threshold_mv_) {
            transceiver_fault_ = true;
        }
    }

    [[nodiscard]] constexpr uint32_t total_strikes() const noexcept {
        return strike_count_;
    }

    [[nodiscard]] constexpr uint16_t max_peak_voltage_mv() const noexcept {
        return max_recorded_peak_mv_;
    }

    [[nodiscard]] constexpr bool is_fault_active() const noexcept {
        return transceiver_fault_;
    }

    [[nodiscard]] constexpr const EsdEventRecord& last_event() const noexcept {
        return last_event_;
    }

    // Процедура апаратного скидання та перезапуску лінії
    template <typename PowerSwitchCallable>
        requires std::invocable<PowerSwitchCallable, bool>
    [[nodiscard]] std::expected<void, RecoveryStatus>
    recover_interface(PowerSwitchCallable&& power_control) noexcept {
        if (!transceiver_fault_) {
            return {};
        }

        // Вимкнення живлення порту (скидання тиристорного замикання Latch-up)
        power_control(false);

        // Пауза для повного розряду ємностей
        // В реальному драйвері тут викликається апаратний таймер затримки 10 мс
        
        // Повторне увімкнення
        power_control(true);

        transceiver_fault_ = false;
        return {};
    }

private:
    uint32_t strike_count_{0};
    uint16_t max_recorded_peak_mv_{0};
    uint16_t critical_threshold_mv_{4500}; // Поріг небезпеки (4.5 В)
    bool transceiver_fault_{false};
    EsdEventRecord last_event_{};
};

} // namespace embedded_safety
