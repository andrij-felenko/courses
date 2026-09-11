#ifndef AMBIENT_ADAPTOR_HPP_
#define AMBIENT_ADAPTOR_HPP_

#include <cstdint>
#include <array>
#include <algorithm>

namespace laser {

/**
 * @brief Опорна точка таблиці відповідності освітленості та шпаруватості.
 */
struct LuxToDutyPoint {
    uint32_t lux;              // Освітленість у люксах (лк)
    uint16_t duty_permille;    // Цільова шпаруватість ШІМ (0..1000 проміле)
};

/**
 * @brief Модуль адаптації яскравості лазерної лінії під зовнішнє освітлення.
 * 
 * Оскільки сприйняття яскравості матрицею камери підпорядковане логарифмічній шкалі,
 * лінійне регулювання неефективне. Клас використовує попередньо калібровану
 * логарифмічну LUT-таблицю для обчислення оптимального коефіцієнта заповнення.
 */
class AmbientAdaptor {
public:
    // Калібрувальна логарифмічна таблиця для діапазону від 10 лк (темна лабораторія) до 100 000 лк (сонце)
    static constexpr size_t kTableSize = 6;

    explicit AmbientAdaptor(uint16_t min_duty = 100, uint16_t max_duty = 950) noexcept
        : min_duty_permille_(min_duty), max_duty_permille_(max_duty) {}

    /**
     * @brief Розрахунок оптимальної шпаруватості ШІМ за поточним рівнем освітленості.
     * @param current_lux Рівень освітленості від фотодатчика (лк)
     * @return Рекомендована шпаруватість у проміле (0..1000)
     */
    [[nodiscard]] uint16_t calculate_duty(uint32_t current_lux) const noexcept {
        if (current_lux <= kLut[0].lux) {
            return std::max(kLut[0].duty_permille, min_duty_permille_);
        }
        if (current_lux >= kLut[kTableSize - 1].lux) {
            return std::min(kLut[kTableSize - 1].duty_permille, max_duty_permille_);
        }

        // Пошук діапазону та кусково-лінійна інтерполяція в логарифмічній сітці
        for (size_t i = 0; i < kTableSize - 1; ++i) {
            if (current_lux >= kLut[i].lux && current_lux <= kLut[i + 1].lux) {
                const uint32_t delta_lux = kLut[i + 1].lux - kLut[i].lux;
                const int32_t delta_duty = static_cast<int32_t>(kLut[i + 1].duty_permille) -
                                           static_cast<int32_t>(kLut[i].duty_permille);

                const uint32_t offset_lux = current_lux - kLut[i].lux;
                const int32_t interpolated = static_cast<int32_t>(kLut[i].duty_permille) +
                                             static_cast<int32_t>((offset_lux * delta_duty) / delta_lux);

                const auto clamped = std::clamp<int32_t>(interpolated, min_duty_permille_, max_duty_permille_);
                return static_cast<uint16_t>(clamped);
            }
        }

        return min_duty_permille_;
    }

private:
    // Логарифмічні вузли: 10 лк (10%), 100 лк (20%), 1 000 лк (40%), 10 000 лк (65%), 50 000 лк (85%), 100 000 лк (95%)
    static constexpr std::array<LuxToDutyPoint, kTableSize> kLut{{
        {10, 100},
        {100, 200},
        {1000, 400},
        {10000, 650},
        {50000, 850},
        {100000, 950}
    }};

    uint16_t min_duty_permille_{100};
    uint16_t max_duty_permille_{950};
};

} // namespace laser

#endif // AMBIENT_ADAPTOR_HPP_
