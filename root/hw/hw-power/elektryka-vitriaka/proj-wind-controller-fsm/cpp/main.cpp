#include <chrono>
#include <cstdint>
#include <concepts>
#include <algorithm>
#include <optional>

namespace wind {

using namespace std::chrono_literals;

/* Суворо типізовані одиниці фізичних величин */
struct Millivolts {
    uint16_t value{0};
    constexpr auto operator<=>(const Millivolts&) const = default;
};

struct Milliamps {
    uint16_t value{0};
    constexpr auto operator<=>(const Milliamps&) const = default;
};

struct RotationsPerMinute {
    uint16_t value{0};
    constexpr auto operator<=>(const RotationsPerMinute&) const = default;
};

struct Permille {
    uint16_t value{0}; // 0 .. 1000 (0.0% .. 100.0%)
    constexpr auto operator<=>(const Permille&) const = default;
};

enum class WindState : uint8_t {
    ParkedBraked = 0,
    StartupRelease,
    MpptTracking,
    PowerLimitDump,
    HighWindBraking,
    FaultLatch
};

enum class WindFault : uint8_t {
    None = 0,
    BatteryOvervoltage,
    RotorOverspeed,
    HeatsinkOvertemp
};

struct TurbineLimits {
    Millivolts vbat_nominal{48000};
    Millivolts vbat_float_target{54400};
    Millivolts vbat_absorption_max{57600};
    Millivolts vbat_alarm_cutoff{60000};

    RotationsPerMinute rpm_cut_in{120};
    RotationsPerMinute rpm_rated{450};
    RotationsPerMinute rpm_overspeed{550};
    RotationsPerMinute rpm_safe_brake{200};
};

struct IWindHardware {
    virtual ~IWindHardware() = default;
    virtual void set_mppt_pwm(Permille duty) = 0;
    virtual void set_dump_pwm(Permille duty) = 0;
    virtual void set_short_circuit_relay(bool closed) = 0;
};

class WindTurbineController {
public:
    explicit WindTurbineController(IWindHardware& hw, TurbineLimits limits = {})
        : hw_(hw), limits_(limits)
    {
        apply_hardware_outputs();
    }

    void process(RotationsPerMinute raw_rpm,
                 Millivolts raw_vbat,
                 Millivolts raw_vgen,
                 Milliamps raw_igen,
                 bool heatsink_temp_ok,
                 std::chrono::milliseconds now)
    {
        // IIR-фільтрація вимірювань
        filtered_rpm_.value  = static_cast<uint16_t>((static_cast<uint32_t>(filtered_rpm_.value) * 3U + raw_rpm.value) / 4U);
        filtered_vbat_.value = static_cast<uint16_t>((static_cast<uint32_t>(filtered_vbat_.value) * 3U + raw_vbat.value) / 4U);
        filtered_vgen_.value = static_cast<uint16_t>((static_cast<uint32_t>(filtered_vgen_.value) * 3U + raw_vgen.value) / 4U);

        // Перевірка аварійних умов
        if (!heatsink_temp_ok) {
            trigger_fault(WindFault::HeatsinkOvertemp, now);
            return;
        }
        if (filtered_vbat_ > limits_.vbat_alarm_cutoff) {
            trigger_fault(WindFault::BatteryOvervoltage, now);
            return;
        }
        if (filtered_rpm_ > limits_.rpm_overspeed && state_ != WindState::HighWindBraking) {
            transition_to(WindState::HighWindBraking, now);
            return;
        }

        switch (state_) {
        case WindState::ParkedBraked:
            break;

        case WindState::StartupRelease:
            if (filtered_rpm_ >= limits_.rpm_cut_in) {
                transition_to(WindState::MpptTracking, now);
            }
            break;

        case WindState::MpptTracking:
            if (filtered_rpm_ < RotationsPerMinute{static_cast<uint16_t>(limits_.rpm_cut_in.value - 20U)}) {
                transition_to(WindState::StartupRelease, now);
                break;
            }

            if (filtered_vbat_ >= limits_.vbat_float_target || filtered_rpm_ >= limits_.rpm_rated) {
                transition_to(WindState::PowerLimitDump, now);
                break;
            }

            if ((now - last_mppt_time_) >= 100ms) {
                last_mppt_time_ = now;
                update_cubic_mppt();
            }
            break;

        case WindState::PowerLimitDump:
            update_dump_regulation();
            break;

        case WindState::HighWindBraking:
            if (filtered_rpm_ <= limits_.rpm_safe_brake || (now - state_entry_time_) > 5000ms) {
                hw_.set_short_circuit_relay(true);
                transition_to(WindState::ParkedBraked, now);
            }
            break;

        case WindState::FaultLatch:
            break;
        }
    }

    [[nodiscard]] WindState state() const noexcept { return state_; }
    [[nodiscard]] WindFault fault() const noexcept { return fault_; }
    [[nodiscard]] RotationsPerMinute filtered_rpm() const noexcept { return filtered_rpm_; }
    [[nodiscard]] Millivolts filtered_vbat() const noexcept { return filtered_vbat_; }

private:
    void transition_to(WindState new_state, std::chrono::milliseconds now)
    {
        state_ = new_state;
        state_entry_time_ = now;
        apply_hardware_outputs();
    }

    void trigger_fault(WindFault fault, std::chrono::milliseconds now)
    {
        fault_ = fault;
        transition_to(WindState::FaultLatch, now);
    }

    void apply_hardware_outputs()
    {
        switch (state_) {
        case WindState::ParkedBraked:
        case WindState::FaultLatch:
            mppt_duty_ = Permille{0};
            dump_duty_ = Permille{1000};
            hw_.set_mppt_pwm(mppt_duty_);
            hw_.set_dump_pwm(dump_duty_);
            hw_.set_short_circuit_relay(true);
            break;

        case WindState::StartupRelease:
            mppt_duty_ = Permille{0};
            dump_duty_ = Permille{0};
            hw_.set_mppt_pwm(mppt_duty_);
            hw_.set_dump_pwm(dump_duty_);
            hw_.set_short_circuit_relay(false);
            break;

        case WindState::MpptTracking:
            dump_duty_ = Permille{0};
            hw_.set_dump_pwm(dump_duty_);
            hw_.set_short_circuit_relay(false);
            break;

        case WindState::PowerLimitDump:
            hw_.set_short_circuit_relay(false);
            break;

        case WindState::HighWindBraking:
            mppt_duty_ = Permille{0};
            dump_duty_ = Permille{1000};
            hw_.set_mppt_pwm(mppt_duty_);
            hw_.set_dump_pwm(dump_duty_);
            hw_.set_short_circuit_relay(false);
            break;
        }
    }

    void update_cubic_mppt()
    {
        if (filtered_rpm_ < limits_.rpm_cut_in) {
            mppt_duty_ = Permille{0};
        } else {
            const auto span = static_cast<uint32_t>(limits_.rpm_rated.value - limits_.rpm_cut_in.value);
            auto delta = static_cast<uint32_t>(filtered_rpm_.value - limits_.rpm_cut_in.value);
            delta = std::min(delta, span);
            const uint32_t target = (delta * delta * delta) / (span * span / 1000U);
            mppt_duty_ = Permille{static_cast<uint16_t>(std::min(target, 1000U))};
        }
        hw_.set_mppt_pwm(mppt_duty_);
    }

    void update_dump_regulation()
    {
        if (filtered_vbat_ > limits_.vbat_float_target) {
            const auto err = static_cast<uint32_t>(filtered_vbat_.value - limits_.vbat_float_target.value);
            const auto range = static_cast<uint32_t>(limits_.vbat_absorption_max.value - limits_.vbat_float_target.value);
            const uint32_t duty = (err * 1000U) / range;
            dump_duty_ = Permille{static_cast<uint16_t>(std::min(duty, 1000U))};
        } else {
            dump_duty_ = Permille{0};
            if (filtered_rpm_ < RotationsPerMinute{static_cast<uint16_t>(limits_.rpm_rated.value - 30U)}) {
                transition_to(WindState::MpptTracking, state_entry_time_);
            }
        }
        hw_.set_dump_pwm(dump_duty_);
    }

    IWindHardware& hw_;
    TurbineLimits limits_;
    WindState state_{WindState::ParkedBraked};
    WindFault fault_{WindFault::None};
    std::chrono::milliseconds state_entry_time_{0};
    std::chrono::milliseconds last_mppt_time_{0};

    RotationsPerMinute filtered_rpm_{0};
    Millivolts filtered_vbat_{0};
    Millivolts filtered_vgen_{0};
    Permille mppt_duty_{0};
    Permille dump_duty_{0};
};

} // namespace wind
