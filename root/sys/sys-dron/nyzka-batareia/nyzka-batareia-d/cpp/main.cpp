#include <cstdint>
#include <algorithm>
#include <chrono>

namespace drone::power {

enum class BatteryFailsafeState : uint8_t {
    Normal   = 0,
    Warning  = 1,
    Rtl      = 2,
    Land     = 3
};

struct BatteryConfig {
    uint8_t cell_count{6};
    float   capacity_mah{5000.0f};
    float   r_internal_pack_ohm{0.060f};
    float   filter_time_constant_s{0.8f};

    // Пороги оціненої ЕРС на банку (В)
    float   v_cell_warning{3.65f};
    float   v_cell_rtl{3.55f};
    float   v_cell_land{3.40f};

    // Пороги залишкової ємності (частка 0.0 - 1.0)
    float   soc_warning{0.30f};
    float   soc_rtl{0.20f};
    float   soc_land{0.10f};

    // Час утримання умови для спрацьовування
    std::chrono::milliseconds debounce_warning{5000};
    std::chrono::milliseconds debounce_rtl{3000};
    std::chrono::milliseconds debounce_land{1000};
};

class BatteryFailsafeManager {
public:
    explicit BatteryFailsafeManager(BatteryConfig config) noexcept
        : cfg_(config),
          u_cell_ocv_filtered_(config.v_cell_warning) {}

    BatteryFailsafeState update(float u_pack_raw_v, float i_pack_raw_a, float dt_seconds) noexcept {
        if (cfg_.cell_count == 0) return BatteryFailsafeState::Normal;

        // 1. Інтегрування витрати заряду
        const float delta_mah = (i_pack_raw_a * 1000.0f) * (dt_seconds / 3600.0f);
        consumed_mah_ += delta_mah;
        soc_remaining_ = std::clamp(1.0f - (consumed_mah_ / cfg_.capacity_mah), 0.0f, 1.0f);

        // 2. Компенсація просідання напруги під навантаженням
        const float u_pack_ocv = u_pack_raw_v + (i_pack_raw_a * cfg_.r_internal_pack_ohm);
        const float u_cell_ocv = u_pack_ocv / static_cast<float>(cfg_.cell_count);

        // 3. ФНЧ-фільтрація ЕРС комірки
        if (!initialized_) {
            u_cell_ocv_filtered_ = u_cell_ocv;
            initialized_ = true;
        } else {
            const float alpha = dt_seconds / (cfg_.filter_time_constant_s + dt_seconds);
            u_cell_ocv_filtered_ += alpha * (u_cell_ocv - u_cell_ocv_filtered_);
        }

        // 4. Оцінка порогів окремо за напругою та за кулонометрією
        const auto state_voltage  = evaluate_voltage_thresholds(u_cell_ocv_filtered_);
        const auto state_capacity = evaluate_capacity_thresholds(soc_remaining_);

        // Консервативне об'єднання: вибір найсуворішого рівня
        const auto target_state = std::max(state_voltage, state_capacity);

        // 5. Оновлення таймерів дебаунсу
        const auto dt_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::duration<float>(dt_seconds)
        );

        time_below_land_ = (target_state >= BatteryFailsafeState::Land) ? (time_below_land_ + dt_ms) : std::chrono::milliseconds{0};
        time_below_rtl_  = (target_state >= BatteryFailsafeState::Rtl)  ? (time_below_rtl_ + dt_ms)  : std::chrono::milliseconds{0};
        time_below_warn_ = (target_state >= BatteryFailsafeState::Warning) ? (time_below_warn_ + dt_ms) : std::chrono::milliseconds{0};

        // 6. Фіксована ескалація стану (Latching state machine)
        if (time_below_land_ >= cfg_.debounce_land) {
            current_state_ = BatteryFailsafeState::Land;
        } else if (time_below_rtl_ >= cfg_.debounce_rtl) {
            current_state_ = std::max(current_state_, BatteryFailsafeState::Rtl);
        } else if (time_below_warn_ >= cfg_.debounce_warning) {
            current_state_ = std::max(current_state_, BatteryFailsafeState::Warning);
        }

        return current_state_;
    }

    [[nodiscard]] BatteryFailsafeState state() const noexcept { return current_state_; }
    [[nodiscard]] float cell_ocv_filtered() const noexcept { return u_cell_ocv_filtered_; }
    [[nodiscard]] float remaining_soc() const noexcept { return soc_remaining_; }
    [[nodiscard]] float consumed_capacity_mah() const noexcept { return consumed_mah_; }

private:
    [[nodiscard]] BatteryFailsafeState evaluate_voltage_thresholds(float v_cell) const noexcept {
        if (v_cell <= cfg_.v_cell_land)    return BatteryFailsafeState::Land;
        if (v_cell <= cfg_.v_cell_rtl)     return BatteryFailsafeState::Rtl;
        if (v_cell <= cfg_.v_cell_warning) return BatteryFailsafeState::Warning;
        return BatteryFailsafeState::Normal;
    }

    [[nodiscard]] BatteryFailsafeState evaluate_capacity_thresholds(float soc) const noexcept {
        if (soc <= cfg_.soc_land)    return BatteryFailsafeState::Land;
        if (soc <= cfg_.soc_rtl)     return BatteryFailsafeState::Rtl;
        if (soc <= cfg_.soc_warning) return BatteryFailsafeState::Warning;
        return BatteryFailsafeState::Normal;
    }

    BatteryConfig cfg_;
    float u_cell_ocv_filtered_{0.0f};
    float consumed_mah_{0.0f};
    float soc_remaining_{1.0f};

    std::chrono::milliseconds time_below_warn_{0};
    std::chrono::milliseconds time_below_rtl_{0};
    std::chrono::milliseconds time_below_land_{0};

    BatteryFailsafeState current_state_{BatteryFailsafeState::Normal};
    bool initialized_{false};
};

} // namespace drone::power
