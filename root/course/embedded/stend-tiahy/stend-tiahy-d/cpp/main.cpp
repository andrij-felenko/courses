#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <numeric>
#include <expected>
#include <numbers>

namespace thrust_stand {

enum class ProcessingError : uint8_t {
    InvalidCalibration,
    ZeroDivision,
    SensorFault
};

struct ThrustCalibration {
    float scale_counts_per_gram{1.0f};
    float tare_offset_raw{0.0f};
    float temp_coeff_zero{0.0f};      // г/°C
    float base_temp_c{25.0f};
    float shunt_resistor_ohms{0.001f}; // 1 мОм
    float arm_ratio{1.0f};            // L2 / L1
};

struct RawSensorFrame {
    float raw_thrust_counts{0.0f};
    float bus_voltage_v{0.0f};
    float shunt_voltage_mv{0.0f};
    float rotor_rpm{0.0f};
    float sensor_temp_c{25.0f};
    uint32_t timestamp_ms{0};
};

struct ProcessedThrustPoint {
    float thrust_grams{0.0f};
    float thrust_newtons{0.0f};
    float bus_voltage_v{0.0f};
    float current_amperes{0.0f};
    float electrical_power_w{0.0f};
    float rotor_rpm{0.0f};
    float efficiency_gpw{0.0f};       // г/Вт
    float mechanical_torque_nm{0.0f}; // Н·м
};

template <size_t WindowSize = 16>
class ThrustDataProcessor {
public:
    explicit constexpr ThrustDataProcessor(const ThrustCalibration& cal) noexcept
        : cal_(cal) {}

    void set_tare_offset(float tare_raw, float current_temp_c) noexcept {
        cal_.tare_offset_raw = tare_raw;
        cal_.base_temp_c = current_temp_c;
        reset_filter();
    }

    void reset_filter() noexcept {
        ring_buffer_.fill(0.0f);
        ring_idx_ = 0;
        samples_filled_ = 0;
    }

    [[nodiscard]] auto process_frame(const RawSensorFrame& raw) noexcept
        -> std::expected<ProcessedThrustPoint, ProcessingError> {
        
        if (cal_.scale_counts_per_gram <= 0.0f || cal_.shunt_resistor_ohms <= 0.0f) {
            return std::unexpected(ProcessingError::InvalidCalibration);
        }

        // 1. Сира сила з урахуванням тари
        const float counts_diff = raw.raw_thrust_counts - cal_.tare_offset_raw;
        const float uncompensated_grams = counts_diff / cal_.scale_counts_per_gram;

        // 2. Температурна компенсація зміщення
        const float delta_t = raw.sensor_temp_c - cal_.base_temp_c;
        const float temp_offset = delta_t * cal_.temp_coeff_zero;
        const float compensated_grams = uncompensated_grams - temp_offset;

        // 3. Редукція плеча важеля
        const float lever_corrected_g = compensated_grams * cal_.arm_ratio;

        // 4. Ковзне середнє
        const float filtered_thrust_g = apply_filter(lever_corrected_g);

        ProcessedThrustPoint out{};
        out.thrust_grams = filtered_thrust_g;
        out.thrust_newtons = filtered_thrust_g * 0.00980665f;

        // 5. Електричні параметри
        out.bus_voltage_v = raw.bus_voltage_v;
        out.current_amperes = (raw.shunt_voltage_mv * 0.001f) / cal_.shunt_resistor_ohms;
        if (out.current_amperes < 0.0f) out.current_amperes = 0.0f;

        out.electrical_power_w = out.bus_voltage_v * out.current_amperes;
        out.rotor_rpm = raw.rotor_rpm;

        // 6. Питома тяга г/Вт
        if (out.electrical_power_w > 0.05f) {
            out.efficiency_gpw = out.thrust_grams / out.electrical_power_w;
        } else {
            out.efficiency_gpw = 0.0f;
        }

        // 7. Розрахунок механічного моменту tau = P_mech / omega
        constexpr float rpm_to_rad_s = (2.0f * std::numbers::pi_v<float>) / 60.0f;
        const float omega = out.rotor_rpm * rpm_to_rad_s;
        if (omega > 10.0f) {
            constexpr float estimated_motor_eff = 0.80f;
            out.mechanical_torque_nm = (out.electrical_power_w * estimated_motor_eff) / omega;
        } else {
            out.mechanical_torque_nm = 0.0f;
        }

        return out;
    }

private:
    float apply_filter(float val) noexcept {
        ring_buffer_[ring_idx_] = val;
        ring_idx_ = (ring_idx_ + 1) % WindowSize;
        if (samples_filled_ < WindowSize) {
            samples_filled_++;
        }
        const float sum = std::accumulate(ring_buffer_.begin(),
                                          ring_buffer_.begin() + samples_filled_,
                                          0.0f);
        return sum / static_cast<float>(samples_filled_);
    }

    ThrustCalibration cal_;
    std::array<float, WindowSize> ring_buffer_{};
    size_t ring_idx_{0};
    size_t samples_filled_{0};
};

} // namespace thrust_stand
