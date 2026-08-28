#include <cstdint>
#include <array>
#include <optional>
#include <algorithm>

namespace sensing {

struct HallCalibration {
    float sens_v_per_tesla{5.0f};       // Чутливість S0 при 25°C (В/Тл)
    float temp_coeff_alpha{-0.0006f};   // Лінійний ТКЧ (-0.06 %/°C)
    float temp_coeff_beta{0.000002f};   // Квадратичний коефіцієнт
    float t_cal_celsius{25.0f};         // Опорна температура калібрування (°C)
    float coupling_tesla_per_a{0.002f}; // Магнітний зв'язок 2 мТл/А
    float b_op_threshold_mt{15.0f};     // Порог спрацьовування (мТл)
    float b_rp_threshold_mt{10.0f};     // Порог відпускання (мТл)
};

struct MeasurementResult {
    float b_field_mt{0.0f};   // Індукція в мілітеслах
    float current_a{0.0f};    // Струм в амперах
    bool switch_state{false}; // Стан гістерезисного компаратора
};

class PrecisionHallProcessor {
public:
    explicit PrecisionHallProcessor(const HallCalibration& calib = {}, float ema_alpha = 0.2f)
        : calib_(calib), ema_alpha_(std::clamp(ema_alpha, 0.01f, 1.0f)) {}

    void set_zero_offset(float zero_volts) noexcept {
        zero_offset_volts_ = zero_volts;
    }

    [[nodiscard]] float zero_offset() const noexcept {
        return zero_offset_volts_;
    }

    /**
     * Обробка 4 квадратурних фаз напруги обертання струму
     */
    [[nodiscard]] std::optional<MeasurementResult> process(
        const std::array<float, 4>& v_phases,
        float temp_celsius) noexcept
    {
        // 1. Демодуляція 4-фазного обертання струму
        const float v_hall = (v_phases[0] - v_phases[1] + v_phases[2] - v_phases[3]) * 0.25f;
        const float v_signal = v_hall - zero_offset_volts_;

        // 2. Температурна компенсація другого порядку
        const float dt = temp_celsius - calib_.t_cal_celsius;
        float gain_corr = 1.0f + (calib_.temp_coeff_alpha * dt)
                               + (calib_.temp_coeff_beta * dt * dt);
        if (gain_corr < 0.1f) {
            gain_corr = 0.1f;
        }

        const float sens_actual = calib_.sens_v_per_tesla * gain_corr;

        // 3. Індукція магнітного поля та струм
        const float b_tesla = v_signal / sens_actual;
        const float b_mt = b_tesla * 1000.0f;
        const float current_a = (calib_.coupling_tesla_per_a > 1e-9f)
            ? (b_tesla / calib_.coupling_tesla_per_a)
            : 0.0f;

        // 4. Експоненційна фільтрація
        filtered_b_mt_ += ema_alpha_ * (b_mt - filtered_b_mt_);
        filtered_current_a_ += ema_alpha_ * (current_a - filtered_current_a_);

        // 5. Гістерезисний тригер
        if (!switch_state_) {
            if (filtered_b_mt_ >= calib_.b_op_threshold_mt) {
                switch_state_ = true;
            }
        } else {
            if (filtered_b_mt_ <= calib_.b_rp_threshold_mt) {
                switch_state_ = false;
            }
        }

        return MeasurementResult{
            .b_field_mt = filtered_b_mt_,
            .current_a = filtered_current_a_,
            .switch_state = switch_state_
        };
    }

private:
    HallCalibration calib_;
    float zero_offset_volts_{0.0f};
    float filtered_b_mt_{0.0f};
    float filtered_current_a_{0.0f};
    float ema_alpha_{0.2f};
    bool switch_state_{false};
};

} // namespace sensing
