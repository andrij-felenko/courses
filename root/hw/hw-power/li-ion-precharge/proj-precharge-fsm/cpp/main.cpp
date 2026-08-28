#include <chrono>
#include <cstdint>
#include <concepts>
#include <expected>
#include <optional>

namespace power {

using namespace std::chrono_literals;

/* Суворо типізовані одиниці вимірювання для запобігання плутанині */
struct Millivolts {
    uint16_t value{0};
    constexpr auto operator<=>(const Millivolts&) const = default;
};

struct Milliamps {
    uint16_t value{0};
    constexpr auto operator<=>(const Milliamps&) const = default;
};

enum class ChargeState : uint8_t {
    Idle = 0,
    Trickle,
    Precharge,
    ConstantCurrent,
    ConstantVoltage,
    Termination,
    FaultLatch
};

enum class ChargeFault : uint8_t {
    None = 0,
    PrechargeTimeout,
    Overvoltage,
    Overtemperature
};

struct ChargerConfig {
    Millivolts vbat_short_thresh{1500};
    Millivolts vbat_prechg_thresh{3000};
    Millivolts vbat_hysteresis{100};
    Millivolts vbat_target{4200};
    Milliamps current_trickle{30};
    Milliamps current_precharge{150};
    Milliamps current_fast_cc{1000};
    Milliamps current_termination{100};
    std::chrono::milliseconds precharge_timeout{45min};
    std::chrono::milliseconds debounce_delay{200ms};
};

/* Апаратний інтерфейс драйвера силового каскаду за принципом RAII */
class IChargerHardware {
public:
    virtual ~IChargerHardware() = default;
    virtual void set_current_limit(Milliamps ma) = 0;
    virtual void set_voltage_limit(Millivolts mv) = 0;
    virtual void enable_power_stage(bool enable) = 0;
    [[nodiscard]] virtual std::chrono::milliseconds get_steady_time() const = 0;
};

class PrechargeFsmController {
public:
    explicit PrechargeFsmController(IChargerHardware& hw, ChargerConfig cfg = {})
        : hw_{hw}, cfg_{cfg}
    {
        hw_.enable_power_stage(false);
        hw_.set_current_limit(Milliamps{0});
    }

    void process(Millivolts vbat_raw, Milliamps ibat_raw, bool vbus_ok)
    {
        const auto now = hw_.get_steady_time();
        vbus_present_ = vbus_ok;

        /* Експоненційне згладжування шумів АЦП */
        vbat_filtered_.value = static_cast<uint16_t>((static_cast<uint32_t>(vbat_filtered_.value) * 3U + vbat_raw.value) / 4U);
        ibat_filtered_.value = static_cast<uint16_t>((static_cast<uint32_t>(ibat_filtered_.value) * 3U + ibat_raw.value) / 4U);

        if (!vbus_ok) {
            if (state_ != ChargeState::Idle && state_ != ChargeState::FaultLatch) {
                transition_to(ChargeState::Idle, now);
            }
            return;
        }

        const auto time_in_state = now - state_entry_time_;

        switch (state_) {
        case ChargeState::Idle:
            if (vbat_filtered_ < cfg_.vbat_short_thresh) {
                transition_to(ChargeState::Trickle, now);
            } else if (vbat_filtered_ < cfg_.vbat_prechg_thresh) {
                transition_to(ChargeState::Precharge, now);
            } else if (vbat_filtered_ < Millivolts{static_cast<uint16_t>(cfg_.vbat_target.value - 50U)}) {
                transition_to(ChargeState::ConstantCurrent, now);
            }
            break;

        case ChargeState::Trickle:
            if (vbat_filtered_ >= cfg_.vbat_short_thresh) {
                transition_to(ChargeState::Precharge, now);
            }
            break;

        case ChargeState::Precharge:
            if (time_in_state > cfg_.precharge_timeout) {
                fault_ = ChargeFault::PrechargeTimeout;
                transition_to(ChargeState::FaultLatch, now);
                return;
            }

            if (vbat_filtered_ >= Millivolts{static_cast<uint16_t>(cfg_.vbat_prechg_thresh.value + cfg_.vbat_hysteresis.value)}) {
                transition_to(ChargeState::ConstantCurrent, now);
            }
            break;

        case ChargeState::ConstantCurrent:
            if (vbat_filtered_ < Millivolts{static_cast<uint16_t>(cfg_.vbat_prechg_thresh.value - cfg_.vbat_hysteresis.value)}) {
                transition_to(ChargeState::Precharge, now);
                return;
            }

            if (vbat_filtered_ >= cfg_.vbat_target) {
                transition_to(ChargeState::ConstantVoltage, now);
            }
            break;

        case ChargeState::ConstantVoltage:
            if (ibat_filtered_ < cfg_.current_termination && time_in_state > cfg_.debounce_delay) {
                transition_to(ChargeState::Termination, now);
            }
            break;

        case ChargeState::Termination:
            if (vbat_filtered_ < Millivolts{static_cast<uint16_t>(cfg_.vbat_target.value - 150U)}) {
                transition_to(ChargeState::ConstantCurrent, now);
            }
            break;

        case ChargeState::FaultLatch:
            /* Блокування скидається тільки апаратним перезапуском VBUS */
            break;
        }
    }

    [[nodiscard]] ChargeState state() const noexcept { return state_; }
    [[nodiscard]] ChargeFault fault() const noexcept { return fault_; }
    [[nodiscard]] Millivolts filtered_voltage() const noexcept { return vbat_filtered_; }

private:
    void transition_to(ChargeState new_state, std::chrono::milliseconds now)
    {
        state_ = new_state;
        state_entry_time_ = now;

        switch (new_state) {
        case ChargeState::Idle:
            hw_.enable_power_stage(false);
            hw_.set_current_limit(Milliamps{0});
            break;

        case ChargeState::Trickle:
            hw_.set_voltage_limit(cfg_.vbat_prechg_thresh);
            hw_.set_current_limit(cfg_.current_trickle);
            hw_.enable_power_stage(true);
            break;

        case ChargeState::Precharge:
            hw_.set_voltage_limit(cfg_.vbat_prechg_thresh);
            hw_.set_current_limit(cfg_.current_precharge);
            hw_.enable_power_stage(true);
            break;

        case ChargeState::ConstantCurrent:
            hw_.set_voltage_limit(cfg_.vbat_target);
            hw_.set_current_limit(cfg_.current_fast_cc);
            hw_.enable_power_stage(true);
            break;

        case ChargeState::ConstantVoltage:
            hw_.set_voltage_limit(cfg_.vbat_target);
            hw_.set_current_limit(cfg_.current_fast_cc);
            hw_.enable_power_stage(true);
            break;

        case ChargeState::Termination:
        case ChargeState::FaultLatch:
            hw_.enable_power_stage(false);
            hw_.set_current_limit(Milliamps{0});
            break;
        }
    }

    IChargerHardware& hw_;
    ChargerConfig cfg_;
    ChargeState state_{ChargeState::Idle};
    ChargeFault fault_{ChargeFault::None};
    std::chrono::milliseconds state_entry_time_{0};
    Millivolts vbat_filtered_{0};
    Milliamps ibat_filtered_{0};
    bool vbus_present_{false};
};

} // namespace power
