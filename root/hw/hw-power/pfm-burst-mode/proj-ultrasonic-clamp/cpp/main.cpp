#include <cstdint>
#include <span>
#include <concepts>
#include <algorithm>

enum class PowerMode : uint8_t {
    PwmContinuous,
    BurstUltrasonic,
    BurstDeepSleep
};

struct SupervisorConfig {
    uint32_t target_voltage_mv{3300};
    uint32_t hysteresis_mv{30};
    uint32_t min_clamp_freq_hz{26300};
    uint32_t clamp_timeout_us{1000000 / min_clamp_freq_hz}; /* 38 мкс */
    uint32_t pwm_threshold_ua{50000};                       /* 50 мА */
    uint32_t deep_sleep_threshold_ua{20};                   /* 20 мкА */
    uint32_t ovp_offset_mv{120};                            /* Поріг OVP */
};

class UltrasonicPowerSupervisor {
public:
    explicit constexpr UltrasonicPowerSupervisor(SupervisorConfig cfg) noexcept
        : config_(cfg) {}

    struct StepAction {
        bool enable_gate_drivers{false};
        uint8_t pulses_to_dispatch{0};
        uint32_t peak_current_target_ma{0};
        PowerMode current_mode{PowerMode::PwmContinuous};
        bool ovp_triggered{false};
    };

    [[nodiscard]] StepAction process_cycle(uint32_t v_out_mv, uint32_t i_load_ua, uint32_t dt_us) noexcept {
        const uint32_t v_high = config_.target_voltage_mv + config_.hysteresis_mv;
        const uint32_t v_low  = config_.target_voltage_mv - config_.hysteresis_mv;
        const uint32_t v_ovp  = config_.target_voltage_mv + config_.ovp_offset_mv;

        /* Захист від перевищення напруги (OVP) */
        if (v_out_mv >= v_ovp) {
            sleep_timer_us_ = 0;
            return {.enable_gate_drivers = false, .pulses_to_dispatch = 0,
                    .peak_current_target_ma = 0, .current_mode = mode_, .ovp_triggered = true};
        }

        /* Автоматичний вибір макрорежиму */
        if (i_load_ua > config_.pwm_threshold_ua) {
            mode_ = PowerMode::PwmContinuous;
            sleep_timer_us_ = 0;
            return {.enable_gate_drivers = true, .pulses_to_dispatch = 1,
                    .peak_current_target_ma = 1200, .current_mode = mode_, .ovp_triggered = false};
        }

        mode_ = (i_load_ua < config_.deep_sleep_threshold_ua)
                ? PowerMode::BurstDeepSleep
                : PowerMode::BurstUltrasonic;

        /* Перевірка стану компаратора */
        if (v_out_mv >= v_high) {
            sleep_timer_us_ += dt_us;
            if (mode_ == PowerMode::BurstUltrasonic && sleep_timer_us_ >= config_.clamp_timeout_us) {
                sleep_timer_us_ = 0;
                return {.enable_gate_drivers = true, .pulses_to_dispatch = 1,
                        .peak_current_target_ma = 180, .current_mode = mode_, .ovp_triggered = false};
            }
            return {.enable_gate_drivers = false, .pulses_to_dispatch = 0,
                    .peak_current_target_ma = 0, .current_mode = mode_, .ovp_triggered = false};
        }

        if (v_out_mv <= v_low) {
            sleep_timer_us_ = 0;
            const uint8_t pulse_count = (mode_ == PowerMode::BurstDeepSleep) ? 10 : 4;
            return {.enable_gate_drivers = true, .pulses_to_dispatch = pulse_count,
                    .peak_current_target_ma = 450, .current_mode = mode_, .ovp_triggered = false};
        }

        /* Напруга всередині вікна регулювання */
        sleep_timer_us_ += dt_us;
        if (mode_ == PowerMode::BurstUltrasonic && sleep_timer_us_ >= config_.clamp_timeout_us) {
            sleep_timer_us_ = 0;
            return {.enable_gate_drivers = true, .pulses_to_dispatch = 1,
                    .peak_current_target_ma = 180, .current_mode = mode_, .ovp_triggered = false};
        }

        return {.enable_gate_drivers = false, .pulses_to_dispatch = 0,
                .peak_current_target_ma = 0, .current_mode = mode_, .ovp_triggered = false};
    }

    [[nodiscard]] constexpr PowerMode active_mode() const noexcept { return mode_; }

private:
    SupervisorConfig config_;
    PowerMode mode_{PowerMode::PwmContinuous};
    uint32_t sleep_timer_us_{0};
};
