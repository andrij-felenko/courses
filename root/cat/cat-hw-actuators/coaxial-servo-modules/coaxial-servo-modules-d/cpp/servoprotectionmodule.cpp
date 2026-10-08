#include <algorithm>
#include <cstdint>

class ServoProtectionModule {
public:
    struct Config {
        float v_bus_max_volts{52.0f};
        float temp_critical_c{95.0f};
        float temp_warn_c{75.0f};
        float i_q_nominal_max_amp{30.0f};
    };

    struct Telemetry {
        float v_bus_volts{0.0f};
        float temp_stator_c{0.0f};
        float temp_mosfet_c{0.0f};
        float i_q_target_amp{0.0f};
        bool brake_resistor_active{false};
    };

    explicit ServoProtectionModule(Config config) : config_(config) {}

    void process(Telemetry& telemetry) {
        // Захист від перенапруги зворотної ЕРС
        telemetry.brake_resistor_active = (telemetry.v_bus_volts > config_.v_bus_max_volts);

        // Теплове дроТлювання струму (Thermal Throttling)
        const float max_temp = std::max(telemetry.temp_stator_c, telemetry.temp_mosfet_c);
        float current_limit = config_.i_q_nominal_max_amp;

        if (max_temp >= config_.temp_critical_c) {
            current_limit = 0.0f;
        } else if (max_temp > config_.temp_warn_c) {
            const float scale = (config_.temp_critical_c - max_temp) / 
                                (config_.temp_critical_c - config_.temp_warn_c);
            current_limit = config_.i_q_nominal_max_amp * scale;
        }

        telemetry.i_q_target_amp = std::clamp(telemetry.i_q_target_amp, -current_limit, current_limit);
    }

private:
    Config config_;
};
