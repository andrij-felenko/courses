#ifndef THERMAL_GUARD_HPP_
#define THERMAL_GUARD_HPP_

#include <cstdint>
#include <algorithm>

namespace laser {

/**
 * @brief Математична модель теплового балансу напівпровідникового лазерного діода.
 * 
 * Реалізує алгоритм дірявого відра (leaky bucket):
 * Кожен спалах або період активного випромінювання наповнює віртуальне відро теплом,
 * пропорційно до енергії імпульсу. Одночасно тепло постійно витікає зі швидкістю,
 * еквівалентною тепловому розсіюванню алюмінієвого радіатора модуля.
 * При досягненні 80% порогу активується тротлінг, а при 100% - захисне відключення.
 */
class ThermalGuard {
public:
    struct Parameters {
        uint32_t bucket_capacity{100000};      // Максимальна теплоємність радіатора (умовні одиниці)
        uint32_t cooling_rate_per_sec{20000};  // Швидкість охолодження (одиниць за секунду)
        uint16_t throttle_threshold_pct{80};   // Поріг активації обмеження потужності (80%)
        uint16_t max_safe_duty_permille{400};  // Обмеження шпаруватості в режимі тротлінгу (40%)
    };

    explicit ThermalGuard(const Parameters& params = {}) noexcept
        : params_(params) {}

    /**
     * @brief Оновлення теплового стану на основі монотонного системного часу.
     * @param current_time_ms Поточний системний час у мілісекундах
     */
    void update(uint32_t current_time_ms) noexcept {
        if (last_update_ms_ == 0) {
            last_update_ms_ = current_time_ms;
            return;
        }

        const uint32_t elapsed_ms = current_time_ms - last_update_ms_;
        if (elapsed_ms == 0) return;

        // Витік тепла (розсіювання у навколишнє середовище)
        const uint32_t leaked_heat = (params_.cooling_rate_per_sec * elapsed_ms) / 1000UL;
        if (leaked_heat >= heat_level_) {
            heat_level_ = 0;
        } else {
            heat_level_ -= leaked_heat;
        }

        last_update_ms_ = current_time_ms;
    }

    /**
     * @brief Додавання енергії виконаного спалаху до теплового балансу.
     * @param duration_us Тривалість імпульсу у мікросекундах
     * @param duty_permille Шпаруватість випромінювання під час імпульсу (0..1000)
     */
    void register_pulse(uint32_t duration_us, uint16_t duty_permille) noexcept {
        // Тепловий внесок = час * відносна потужність
        const uint32_t heat_added = (duration_us * static_cast<uint32_t>(duty_permille)) / 1000UL;
        heat_level_ = std::min(params_.bucket_capacity, heat_level_ + heat_added);
    }

    /**
     * @brief Коригування запропонованої шпаруватості відповідно до теплового стану.
     * Якщо кристал перегрівається, шпаруватість примусово занижується.
     */
    [[nodiscard]] uint16_t clamp_duty(uint16_t requested_duty) const noexcept {
        if (is_critical_overheat()) {
            return 0; // Повне відключення при 100% заповненні теплового бюджету
        }
        if (is_throttling()) {
            return std::min(requested_duty, params_.max_safe_duty_permille);
        }
        return requested_duty;
    }

    [[nodiscard]] uint16_t thermal_load_percent() const noexcept {
        return static_cast<uint16_t>((heat_level_ * 100UL) / params_.bucket_capacity);
    }

    [[nodiscard]] bool is_throttling() const noexcept {
        return thermal_load_percent() >= params_.throttle_threshold_pct;
    }

    [[nodiscard]] bool is_critical_overheat() const noexcept {
        return heat_level_ >= params_.bucket_capacity;
    }

    void reset() noexcept {
        heat_level_ = 0;
        last_update_ms_ = 0;
    }

private:
    Parameters params_{};
    uint32_t heat_level_{0};          // Поточний накопичений рівень тепла у відрі
    uint32_t last_update_ms_{0};
};

} // namespace laser

#endif // THERMAL_GUARD_HPP_
