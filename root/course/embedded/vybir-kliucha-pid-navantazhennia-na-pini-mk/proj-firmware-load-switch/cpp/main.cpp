#include <cstdint>
#include <algorithm>
#include <concepts>

namespace embedded::power {

enum class SwitchState : uint8_t {
    Off = 0,
    RampingUp,
    Running,
    RampingDown,
    FaultTimeout
};

/* Концепт для апаратного рівня доступу до портів введення-виведення */
template <typename T>
concept HardwarePortPolicy = requires(T policy, uint32_t val) {
    { policy.force_low() } noexcept;
    { policy.write_pwm(val) } noexcept;
};

/* Ідіоматичний RAII-драйвер силового ключа */
template <HardwarePortPolicy Policy>
class LoadSwitch {
public:
    constexpr LoadSwitch(Policy port_policy, uint32_t timer_arr, uint32_t step_ramp = 15) noexcept
        : policy_(port_policy), timer_arr_(timer_arr), step_increment_(step_ramp) {
        /* При створенні об'єкта RAII гарантує безпечне вимкнення затвора */
        policy_.force_low();
        policy_.write_pwm(0);
    }

    /* Деструктор RAII: гарантовано знеструмлює навантаження при виході з області видимості */
    ~LoadSwitch() noexcept {
        emergency_stop();
    }

    LoadSwitch(const LoadSwitch&) = delete;
    LoadSwitch& operator=(const LoadSwitch&) = delete;
    LoadSwitch(LoadSwitch&&) noexcept = default;
    LoadSwitch& operator=(LoadSwitch&&) noexcept = default;

    /* Встановлення цільової потужності (0..1000 проміле) та таймауту безпеки в мс */
    void set_target(uint16_t permille, uint32_t timeout_ms) noexcept {
        target_duty_ = std::min<uint16_t>(permille, 1000);
        remaining_timeout_ms_ = timeout_ms;
        if (target_duty_ == 0) {
            state_ = SwitchState::RampingDown;
        } else {
            state_ = (current_duty_ < target_duty_) ? SwitchState::RampingUp : SwitchState::RampingDown;
        }
    }

    /* Миттєва зупинка каналу */
    void emergency_stop() noexcept {
        target_duty_ = 0;
        current_duty_ = 0;
        remaining_timeout_ms_ = 0;
        state_ = SwitchState::Off;
        policy_.write_pwm(0);
        policy_.force_low();
    }

    /* Обробник тику системного таймера (1 мс) */
    void update_1ms() noexcept {
        if (remaining_timeout_ms_ > 0) {
            if (--remaining_timeout_ms_ == 0 && target_duty_ > 0) {
                emergency_stop();
                state_ = SwitchState::FaultTimeout;
                return;
            }
        }

        if (current_duty_ != target_duty_) {
            if (current_duty_ < target_duty_) {
                current_duty_ = std::min<uint16_t>(current_duty_ + step_increment_, target_duty_);
            } else {
                current_duty_ = (current_duty_ > step_increment_) ? (current_duty_ - step_increment_) : target_duty_;
            }

            const uint32_t compare_val = (static_cast<uint64_t>(current_duty_) * timer_arr_) / 1000U;
            policy_.write_pwm(compare_val);

            if (current_duty_ == target_duty_) {
                state_ = (target_duty_ > 0) ? SwitchState::Running : SwitchState::Off;
            }
        }
    }

    [[nodiscard]] SwitchState state() const noexcept { return state_; }
    [[nodiscard]] uint16_t current_duty() const noexcept { return current_duty_; }

private:
    Policy policy_;
    const uint32_t timer_arr_;
    const uint32_t step_increment_;
    uint16_t current_duty_{0};
    uint16_t target_duty_{0};
    uint32_t remaining_timeout_ms_{0};
    SwitchState state_{SwitchState::Off};
};

/* Приклад політики керування для апаратного таймера STM32 */
struct Stm32GpioPwmPolicy {
    volatile uint32_t* const bsrr_reg;
    const uint32_t pin_mask;
    volatile uint32_t* const ccr_reg;

    void force_low() const noexcept {
        *bsrr_reg = (pin_mask << 16U);
    }

    void write_pwm(uint32_t compare_val) const noexcept {
        if (ccr_reg != nullptr) {
            *ccr_reg = compare_val;
        }
    }
};

} // namespace embedded::power
