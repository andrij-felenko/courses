#include <cstdint>
#include <array>

namespace sensing {

struct HallConfig {
    float sens_mv_per_mt{25.0f};  // Чутливість (мВ/мТл)
    float temp_coeff_ppm{-600.0f}; // ТКЧ (-600 ppm/°C)
    float v_zero_volts{2.500f};   // Нуль спокою (В)
    float b_op_mt{15.0f};         // Поріг спрацьовування (мТл)
    float b_rp_mt{10.0f};         // Поріг відпускання (мТл)
};

class HallSensorDriver {
public:
    explicit HallSensorDriver(const HallConfig& cfg = {}) : cfg_(cfg) {}

    [[nodiscard]] float process_quad_phases(const std::array<float, 4>& v_phases, float temp_c) noexcept {
        // 4-фазне обертання струму (Spinning Current)
        const float v_hall = (v_phases[0] - v_phases[1] + v_phases[2] - v_phases[3]) * 0.25f;
        const float v_diff_mv = (v_hall - cfg_.v_zero_volts) * 1000.0f;

        // Температурна поправка
        const float dt = temp_c - 25.0f;
        const float sens_comp = cfg_.sens_mv_per_mt * (1.0f + (cfg_.temp_coeff_ppm * 1e-6f * dt));

        current_field_mt_ = (sens_comp > 0.001f) ? (v_diff_mv / sens_comp) : 0.0f;

        // Оновлення стану тригера з гістерезисом
        if (!switch_state_) {
            if (current_field_mt_ >= cfg_.b_op_mt) {
                switch_state_ = true;
            }
        } else {
            if (current_field_mt_ <= cfg_.b_rp_mt) {
                switch_state_ = false;
            }
        }

        return current_field_mt_;
    }

    [[nodiscard]] bool switch_state() const noexcept { return switch_state_; }
    [[nodiscard]] float field_mt() const noexcept { return current_field_mt_; }

private:
    HallConfig cfg_;
    bool switch_state_{false};
    float current_field_mt_{0.0f};
};

} // namespace sensing
