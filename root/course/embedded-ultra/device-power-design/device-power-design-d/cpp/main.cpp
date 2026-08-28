#include <cstdint>
#include <algorithm>

namespace vehicle::power {

/**
 * @brief Стани системи контролю живлення
 */
enum class BatteryState : uint8_t {
    Ok = 0,
    LowWarning,
    Critical,
    EmergencyBrownout
};

/**
 * @brief Параметри конфігурації монітора батареї
 */
struct MonitorConfig {
    uint8_t cell_count{6};             // Кількість банок у послідовному з'єднанні
    float   capacity_mah{5000.0f};     // Номінальна ємність батареї (мАг)
    float   r_internal_total_ohm{0.018f}; // Загальний внутрішній опір збірки (Ом)
    float   cell_warn_mv{3500.0f};     // Поріг тривоги (мВ на банку)
    float   cell_crit_mv{3300.0f};     // Критичний поріг (мВ на банку)
    float   cell_emergency_mv{3000.0f};// Поріг апаратного браунауту (мВ на банку)
    float   filter_alpha_v{0.15f};     // Коефіцієнт фільтра напруги EMA
    float   filter_alpha_i{0.10f};     // Коефіцієнт фільтра струму EMA
    float   dt_sec{0.02f};             // Період оновлення (секунди, 50 Гц)
    uint16_t debounce_limit{150};      // Поріг дебаунсу в тактах (3 с при 50 Гц)
};

/**
 * @brief Зріз виміряних та розрахованих телеметричних даних
 */
struct TelemetrySnapshot {
    float        voltage_filtered_mv{0.0f};
    float        current_filtered_ma{0.0f};
    float        voltage_ocv_est_mv{0.0f};
    float        cell_ocv_mv{0.0f};
    float        consumed_mah{0.0f};
    float        remaining_percent{100.0f};
    BatteryState state{BatteryState::Ok};
};

/**
 * @brief Клас драйвера моніторингу та захисту батареї
 */
class BatteryMonitor {
public:
    constexpr explicit BatteryMonitor(const MonitorConfig& config) noexcept
        : cfg_(config) {}

    /**
     * @brief Крок оновлення стану монітора
     * @param raw_voltage_mv Напруга на клемах акумулятора (мВ)
     * @param raw_current_ma Струм споживання через шунт (мА)
     * @return Поточний оцінений стан безпеки
     */
    BatteryState update(float raw_voltage_mv, float raw_current_ma) noexcept {
        if (!initialized_) {
            v_filt_mv_ = raw_voltage_mv;
            i_filt_ma_ = raw_current_ma;
            initialized_ = true;
        } else {
            // Цифрова фільтрація шумів комутації
            v_filt_mv_ = cfg_.filter_alpha_v * raw_voltage_mv + 
                         (1.0f - cfg_.filter_alpha_v) * v_filt_mv_;
            i_filt_ma_ = cfg_.filter_alpha_i * raw_current_ma + 
                         (1.0f - cfg_.filter_alpha_i) * i_filt_ma_;
        }

        // Враховуємо лише прямий струм розряду
        const float active_current = std::max(0.0f, i_filt_ma_);

        // Інтегрування витраченого заряду
        const float mah_delta = (active_current * cfg_.dt_sec) / 3600.0f;
        consumed_mah_ += mah_delta;

        if (cfg_.capacity_mah > 0.0f) {
            const float rem = (cfg_.capacity_mah - consumed_mah_) / cfg_.capacity_mah * 100.0f;
            remaining_pct_ = std::clamp(rem, 0.0f, 100.0f);
        }

        // Розрахунок компенсації омічного просідання: V_ocv = V_term + I · R_int
        const float v_drop_mv = active_current * cfg_.r_internal_total_ohm;
        v_ocv_mv_ = v_filt_mv_ + v_drop_mv;

        cell_ocv_mv_ = (cfg_.cell_count > 0) ? (v_ocv_mv_ / static_cast<float>(cfg_.cell_count))
                                             : v_ocv_mv_;

        update_state_machine();
        return state_;
    }

    [[nodiscard]] TelemetrySnapshot snapshot() const noexcept {
        return { v_filt_mv_, i_filt_ma_, v_ocv_mv_, cell_ocv_mv_, consumed_mah_, remaining_pct_, state_ };
    }

    [[nodiscard]] BatteryState state() const noexcept { return state_; }
    [[nodiscard]] float cell_ocv_mv() const noexcept { return cell_ocv_mv_; }
    [[nodiscard]] float remaining_percent() const noexcept { return remaining_pct_; }

private:
    void update_state_machine() noexcept {
        if (cell_ocv_mv_ <= cfg_.cell_emergency_mv) {
            state_ = BatteryState::EmergencyBrownout;
            return;
        }

        if (cell_ocv_mv_ <= cfg_.cell_crit_mv) {
            if (++crit_ticks_ >= cfg_.debounce_limit) {
                state_ = BatteryState::Critical;
            }
        } else if (cell_ocv_mv_ <= cfg_.cell_warn_mv) {
            crit_ticks_ = 0;
            if (++warn_ticks_ >= cfg_.debounce_limit) {
                state_ = BatteryState::LowWarning;
            }
        } else {
            if (warn_ticks_ > 0) --warn_ticks_;
            if (crit_ticks_ > 0) --crit_ticks_;
            if (warn_ticks_ == 0 && crit_ticks_ == 0) {
                state_ = BatteryState::Ok;
            }
        }
    }

    MonitorConfig cfg_;
    float         v_filt_mv_{0.0f};
    float         i_filt_ma_{0.0f};
    float         v_ocv_mv_{0.0f};
    float         cell_ocv_mv_{0.0f};
    float         consumed_mah_{0.0f};
    float         remaining_pct_{100.0f};
    BatteryState  state_{BatteryState::Ok};
    uint16_t      warn_ticks_{0};
    uint16_t      crit_ticks_{0};
    bool          initialized_{false};
};

} // namespace vehicle::power
