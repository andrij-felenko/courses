/* Контролер формування імпульсів силового драйвера GTO (C++20) */
#include <cstdint>
#include <chrono>
#include <concepts>

enum class DriverState : uint8_t {
    OffNegativeBias = 0,   // Від'ємне зміщення V_GR (-18 В)
    TurnOnPulse,           // Потужний імпульс увімкнення I_GM (30..50 А)
    OnBackPorch,           // Підтримуюча полиця струму I_G_cont (3..10 А)
    TurnOffExtraction,     // Потужна екстракція дірок -I_GQ (400..800 А)
    FaultLockout           // Аварійне блокування при зриві комутації
};

struct DriverTimingConfig {
    std::chrono::microseconds turn_on_pulse{10};
    std::chrono::microseconds min_on_time{60};
    std::chrono::microseconds turn_off_pulse{25};
    std::chrono::microseconds min_off_time{80};
    std::chrono::microseconds max_storage_timeout{12};
};

class GtoGateDriver {
public:
    explicit constexpr GtoGateDriver(const DriverTimingConfig& config) noexcept
        : config_(config),
          state_(DriverState::OffNegativeBias),
          off_time_accum_(config.min_off_time) {}

    void set_command(bool enable) noexcept {
        command_on_ = enable;
    }

    [[nodiscard]] DriverState state() const noexcept {
        return state_;
    }

    [[nodiscard]] bool has_fault() const noexcept {
        return state_ == DriverState::FaultLockout;
    }

    // Крок дискретизації автомата керування (квант 1 мкс)
    void tick_1us(bool anode_voltage_recovered) noexcept {
        if (state_ == DriverState::FaultLockout) {
            apply_hardware_outputs(false, false, false, true);
            return;
        }

        state_timer_ += std::chrono::microseconds(1);

        switch (state_) {
            case DriverState::OffNegativeBias:
                off_time_accum_ += std::chrono::microseconds(1);
                apply_hardware_outputs(false, false, false, true);

                if (command_on_ && (off_time_accum_ >= config_.min_off_time)) {
                    transition_to(DriverState::TurnOnPulse);
                    on_time_accum_ = std::chrono::microseconds(0);
                }
                break;

            case DriverState::TurnOnPulse:
                on_time_accum_ += std::chrono::microseconds(1);
                apply_hardware_outputs(true, true, false, false);

                if (state_timer_ >= config_.turn_on_pulse) {
                    transition_to(DriverState::OnBackPorch);
                }
                break;

            case DriverState::OnBackPorch:
                on_time_accum_ += std::chrono::microseconds(1);
                apply_hardware_outputs(false, true, false, false);

                if (!command_on_ && (on_time_accum_ >= config_.min_on_time)) {
                    transition_to(DriverState::TurnOffExtraction);
                    off_time_accum_ = std::chrono::microseconds(0);
                }
                break;

            case DriverState::TurnOffExtraction:
                apply_hardware_outputs(false, false, true, false);

                if (state_timer_ > config_.max_storage_timeout && !anode_voltage_recovered) {
                    transition_to(DriverState::FaultLockout);
                    break;
                }

                if (state_timer_ >= config_.turn_off_pulse) {
                    transition_to(DriverState::OffNegativeBias);
                }
                break;

            case DriverState::FaultLockout:
            default:
                apply_hardware_outputs(false, false, false, true);
                break;
        }
    }

    void reset_fault() noexcept {
        if (state_ == DriverState::FaultLockout && !command_on_) {
            transition_to(DriverState::OffNegativeBias);
            off_time_accum_ = config_.min_off_time;
        }
    }

private:
    void transition_to(DriverState next_state) noexcept {
        state_ = next_state;
        state_timer_ = std::chrono::microseconds(0);
    }

    static void apply_hardware_outputs(bool pos_pulse, bool pos_porch, bool neg_pulse, bool neg_bias) noexcept {
        // Апаратний запис у симетричні регістри драйвера
        (void)pos_pulse; (void)pos_porch; (void)neg_pulse; (void)neg_bias;
    }

    DriverTimingConfig config_;
    DriverState state_;
    std::chrono::microseconds state_timer_{0};
    std::chrono::microseconds on_time_accum_{0};
    std::chrono::microseconds off_time_accum_{0};
    bool command_on_{false};
};
