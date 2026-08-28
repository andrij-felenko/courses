#include <cstdint>
#include <concepts>
#include <optional>
#include <span>
#include <array>
#include <chrono>

using namespace std::chrono_literals;

struct PulseResult {
    float v_ds_volts{0.0f};
    float i_d_amperes{0.0f};
    float r_ds_on_ohms{0.0f};
    float energy_joules{0.0f};
};

class PulsedSemiconductorTester {
public:
    static constexpr std::chrono::microseconds kPulseDuration{300us};
    static constexpr std::chrono::microseconds kAdcSamplingDelay{250us};
    static constexpr std::chrono::milliseconds kThermalCooldown{20ms};
    static constexpr float kShuntResistanceOhm{0.010f};
    static constexpr float kAdcReferenceVolts{3.300f};
    static constexpr uint16_t kAdcResolution{4095};
    static constexpr float kMinimumCurrentNoiseThresholdA{0.200f};

    explicit PulsedSemiconductorTester(float current_safety_limit_a)
        : max_current_limit_a_{current_safety_limit_a} {}

    [[nodiscard]] std::optional<PulseResult> acquire_single_pulse(float target_v_gs) const {
        hardware_configure_gate_voltage(target_v_gs);

        // Налаштування та запуск апаратного таймера MCU
        hardware_start_pulse_generator(kPulseDuration.count(), kAdcSamplingDelay.count());
        hardware_wait_pulse_completion();

        const auto [vds_code, shunt_code] = hardware_get_adc_data();

        const float v_ds = (static_cast<float>(vds_code) / kAdcResolution) * kAdcReferenceVolts;
        const float v_shunt = (static_cast<float>(shunt_code) / kAdcResolution) * kAdcReferenceVolts;
        const float i_d = v_shunt / kShuntResistanceOhm;

        // Контроль безпеки кристала
        if (i_d > max_current_limit_a_) {
            hardware_abort_and_isolate();
            return std::nullopt;
        }

        // Пауза термічної релаксації кристала
        hardware_sleep(kThermalCooldown);

        if (i_d < kMinimumCurrentNoiseThresholdA) {
            return std::nullopt;
        }

        const float r_ds = v_ds / i_d;
        const float energy = v_ds * i_d * (kPulseDuration.count() * 1e-6f);

        return PulseResult{
            .v_ds_volts = v_ds,
            .i_d_amperes = i_d,
            .r_ds_on_ohms = r_ds,
            .energy_joules = energy
        };
    }

private:
    float max_current_limit_a_{35.0f};

    // Низькорівневий апаратний драйверний шар
    static void hardware_configure_gate_voltage(float v_gs);
    static void hardware_start_pulse_generator(uint32_t pulse_us, uint32_t trigger_us);
    static void hardware_wait_pulse_completion();
    static std::pair<uint16_t, uint16_t> hardware_get_adc_data();
    static void hardware_abort_and_isolate();
    static void hardware_sleep(std::chrono::milliseconds ms);
};
