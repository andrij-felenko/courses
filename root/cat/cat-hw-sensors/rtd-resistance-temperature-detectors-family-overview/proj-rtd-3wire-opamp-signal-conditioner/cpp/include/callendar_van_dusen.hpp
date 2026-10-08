#ifndef CALLENDAR_VAN_DUSEN_HPP
#define CALLENDAR_VAN_DUSEN_HPP

#include <cmath>
#include <optional>
#include <cstdint>

namespace sensors::rtd {

/**
 * @brief Перелічення типів платинових терморезисторів (RTD).
 */
enum class RtdType : uint8_t {
    Pt100,  ///< Номінальний опір 100.0 Ом при 0 °C
    Pt1000, ///< Номінальний опір 1000.0 Ом при 0 °C
    Custom  ///< Користувацький номінальний опір
};

/**
 * @brief Математичний модуль для обчислення температури за опором платинових терморезисторів.
 *
 * Використовує міжнародне стандартизоване рівняння Каллендара — Ван Дюзена (IEC 60751 / DIN EN 60751):
 * - Для температури t >= 0 °C: R(t) = R0 * (1 + A*t + B*t^2)
 * - Для температури t < 0 °C:  R(t) = R0 * (1 + A*t + B*t^2 + C*(t - 100)*t^3)
 */
class CallendarVanDusen {
public:
    /// Стандартні коефіцієнти для платинового термоопору за IEC 60751 (ITS-90)
    static constexpr double DEFAULT_COEFF_A = 3.9083e-3;   ///< [°C^-1]
    static constexpr double DEFAULT_COEFF_B = -5.775e-7;   ///< [°C^-2]
    static constexpr double DEFAULT_COEFF_C = -4.183e-12;  ///< [°C^-4]

    /**
     * @brief Конструктор за типом терморезистора або з користувацьким опорним опором R0.
     * @param type Тип терморезистора (Pt100, Pt1000 або Custom)
     * @param custom_r0 Значення R0 (Ом), якщо обрано тип Custom
     */
    explicit CallendarVanDusen(RtdType type = RtdType::Pt100, double custom_r0 = 100.0)
        : rtd_type_(type),
          r0_ohms_(type == RtdType::Pt100 ? 100.0 : (type == RtdType::Pt1000 ? 1000.0 : custom_r0)),
          coeff_a_(DEFAULT_COEFF_A),
          coeff_b_(DEFAULT_COEFF_B),
          coeff_c_(DEFAULT_COEFF_C) {}

    /**
     * @brief Конструктор з довільними коефіцієнтами лінеаризації.
     */
    CallendarVanDusen(double r0_ohms, double a, double b, double c)
        : rtd_type_(RtdType::Custom),
          r0_ohms_(r0_ohms),
          coeff_a_(a),
          coeff_b_(b),
          coeff_c_(c) {}

    /**
     * @brief Перетворення виміряного опору (Ом) у температуру (°C).
     * @param resistance_ohms Виміряний та відкалібрований опір датчика.
     * @return Обчислена температура (°C) або std::nullopt у разі невалідного опору.
     */
    [[nodiscard]] std::optional<double> resistanceToTemperature(double resistance_ohms) const {
        if (resistance_ohms <= 0.0 || r0_ohms_ <= 0.0) {
            return std::nullopt;
        }

        const double r_ratio = resistance_ohms / r0_ohms_;

        // Для додатних температур (R >= R0) розв'язуємо аналітичне квадратне рівняння
        if (r_ratio >= 1.0) {
            const double discriminant = coeff_a_ * coeff_a_ - 4.0 * coeff_b_ * (1.0 - r_ratio);
            if (discriminant < 0.0) {
                return std::nullopt;
            }
            return (-coeff_a_ + std::sqrt(discriminant)) / (2.0 * coeff_b_);
        }

        // Для від'ємних температур (R < R0) використовуємо чисельний метод Ньютона — Рафсона
        const double discriminant = coeff_a_ * coeff_a_ - 4.0 * coeff_b_ * (1.0 - r_ratio);
        double temp_c = (discriminant >= 0.0)
            ? (-coeff_a_ + std::sqrt(discriminant)) / (2.0 * coeff_b_)
            : -10.0;

        constexpr int MAX_ITERATIONS = 12;
        constexpr double CONVERGENCE_EPS = 1e-6;

        for (int i = 0; i < MAX_ITERATIONS; ++i) {
            const double t2 = temp_c * temp_c;
            const double t3 = t2 * temp_c;

            const double r_calc = r0_ohms_ * (1.0 + coeff_a_ * temp_c + coeff_b_ * t2 + coeff_c_ * (temp_c - 100.0) * t3);
            const double f_val = r_calc - resistance_ohms;

            if (std::abs(f_val) < CONVERGENCE_EPS) {
                break;
            }

            const double df_dt = r0_ohms_ * (coeff_a_ + 2.0 * coeff_b_ * temp_c + coeff_c_ * (4.0 * t3 - 300.0 * t2));
            if (std::abs(df_dt) < 1e-12) {
                break;
            }

            temp_c -= f_val / df_dt;
        }

        return temp_c;
    }

    /**
     * @brief Розрахунок теоретичного опору (Ом) за заданою температурою (°C).
     * @param temp_c Температура у градусах Цельсія.
     * @return Теоретичне значення опору датчика.
     */
    [[nodiscard]] double temperatureToResistance(double temp_c) const {
        if (temp_c >= 0.0) {
            return r0_ohms_ * (1.0 + coeff_a_ * temp_c + coeff_b_ * temp_c * temp_c);
        }
        const double t2 = temp_c * temp_c;
        const double t3 = t2 * temp_c;
        return r0_ohms_ * (1.0 + coeff_a_ * temp_c + coeff_b_ * t2 + coeff_c_ * (temp_c - 100.0) * t3);
    }

    [[nodiscard]] double getR0() const { return r0_ohms_; }
    [[nodiscard]] RtdType getType() const { return rtd_type_; }
    [[nodiscard]] double getCoeffA() const { return coeff_a_; }
    [[nodiscard]] double getCoeffB() const { return coeff_b_; }
    [[nodiscard]] double getCoeffC() const { return coeff_c_; }

private:
    RtdType rtd_type_{RtdType::Pt100};
    double r0_ohms_{100.0};
    double coeff_a_{DEFAULT_COEFF_A};
    double coeff_b_{DEFAULT_COEFF_B};
    double coeff_c_{DEFAULT_COEFF_C};
};

} // namespace sensors::rtd

#endif // CALLENDAR_VAN_DUSEN_HPP
