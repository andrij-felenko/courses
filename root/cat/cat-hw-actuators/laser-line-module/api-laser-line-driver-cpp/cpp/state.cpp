// laser_line_driver.hpp
#pragma once

#include <cstdint>
#include <atomic>
#include <algorithm>

namespace Laser {

enum class State : uint8_t {
    Init = 0,
    Ready,
    Emitting,
    FaultLockout
};

namespace Error {
    constexpr uint32_t None            = 0;
    constexpr uint32_t WatchdogTimeout = (1 << 0);
    constexpr uint32_t Overheat        = (1 << 1);
    constexpr uint32_t SyncLost        = (1 << 2);
    constexpr uint32_t HardwareError   = (1 << 3);
}

// Абстракція апаратної периферії для детермінованого тестування та перенесення між МК
class ILaserHal {
public:
    virtual void set_pin_state(bool high) = 0;
    virtual void configure_pwm(uint32_t frequency_hz, float duty_percent) = 0;
    virtual void enable_pwm_output(bool enable) = 0;
    virtual void arm_strobe_timer(uint32_t duration_us) = 0;
    virtual void cancel_strobe_timer() = 0;
    virtual void arm_watchdog_timer(uint32_t timeout_us) = 0;
    virtual void reload_watchdog_timer(uint32_t timeout_us) = 0;
    virtual void cancel_watchdog_timer() = 0;
    virtual ~ILaserHal() = default;
};

class LaserLineDriver {
public:
    explicit LaserLineDriver(ILaserHal& hal, uint32_t max_allowed_strobe_us = 25000);

    // Ініціалізація периферії, безпечний перехід у стан Ready
    bool init(uint32_t pwm_frequency_hz = 30000);

    // Налаштування параметрів оптичного випромінювання на льоту
    void set_optical_parameters(float brightness_percent);

    // Асинхронний запуск стробу експозиції
    bool trigger_strobe_async(uint32_t strobe_duration_us);

    // Примусове дострокове завершення стробу
    void cancel_strobe();

    // Підтвердження життєздатності з боку потоку комп'ютерного зору
    void pet_safety_watchdog();

    // Обробники апаратних переривань
    void on_strobe_timer_isr();
    void on_watchdog_timeout_isr();

    // Фіксація апаратного збою (наприклад, перегрів або відмова живлення)
    void report_hardware_fault(uint32_t error_flag);

    // Захищене скидання аварійного блокування
    bool failsafe_reset();

    // Діагностичні методи
    State get_state() const;
    uint32_t get_error_code() const;
    bool is_locked() const;

private:
    void enter_fault_lockout(uint32_t error_flag);

    ILaserHal& hal_;
    const uint32_t max_strobe_us_;
    uint32_t pwm_freq_hz_;
    float current_brightness_;

    std::atomic<State> state_;
    std::atomic<uint32_t> errors_;
};

} // namespace Laser
