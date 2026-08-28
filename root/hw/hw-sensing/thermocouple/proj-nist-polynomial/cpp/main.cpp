#include <array>
#include <span>
#include <cmath>
#include <expected>
#include <concepts>

namespace sensing {

enum class ThermocoupleError {
    ColdJunctionOutOfRange,
    VoltageOutOfRange,
    SensorBurnout
};

enum class ThermocoupleType {
    TypeK,
    TypeJ
};

class NistThermocoupleCalculator {
public:
    /* Схема Горнера для constexpr-масивів коефіцієнтів */
    template <std::floating_point T>
    [[nodiscard]] static constexpr T horner_eval(std::span<const T> coeffs, T x) noexcept {
        T result = coeffs.back();
        for (auto it = coeffs.rbegin() + 1; it != coeffs.rend(); ++it) {
            result = result * x + *it;
        }
        return result;
    }

    /* Прямий поліном NIST Type K: T (°C) -> V (мВ) */
    [[nodiscard]] static double type_k_temp_to_mv(double temp_c) noexcept {
        if (temp_c < 0.0) {
            static constexpr std::array<double, 11> c_neg = {
                0.000000000000E+00,  3.945012802500E-02,  2.362237359800E-05,
               -3.285890678400E-07, -4.990482877700E-09, -6.750905917300E-11,
               -5.741032742800E-13, -3.108894161400E-15, -1.045160936500E-17,
               -1.988926677800E-20, -1.632269748600E-23
            };
            return horner_eval(std::span{c_neg}, temp_c);
        }

        static constexpr std::array<double, 10> c_pos = {
           -1.760041368600E-02,  3.892120497500E-02,  1.855877003200E-05,
           -9.945759287400E-08,  3.184094571900E-10, -5.607284488900E-13,
            5.607505905900E-16, -3.202072444000E-19,  9.715114715200E-23,
           -1.210472127500E-26
        };
        constexpr double a0 = 0.1185976;
        constexpr double a1 = -0.0001183432;
        constexpr double a2 = 126.9686;

        const double base_v = horner_eval(std::span{c_pos}, temp_c);
        const double exp_term = a0 * std::exp(a1 * (temp_c - a2) * (temp_c - a2));
        return base_v + exp_term;
    }

    /* Обернений поліном NIST Type K: V (мВ) -> T (°C) */
    [[nodiscard]] static double type_k_mv_to_temp(double mv) noexcept {
        if (mv < 0.0) {
            static constexpr std::array<double, 9> d_sub1 = {
                0.0000000E+00,  2.5173462E+01, -1.1662878E+00,
               -1.0833638E+00, -8.9773540E-01, -3.7342377E-01,
               -8.6632643E-02, -1.0450598E-02, -5.1920577E-04
            };
            return horner_eval(std::span{d_sub1}, mv);
        } else if (mv <= 20.644) {
            static constexpr std::array<double, 10> d_sub2 = {
                0.000000E+00,  2.508355E+01,  7.860106E-02,
               -2.503131E-01,  8.315270E-02, -1.228034E-02,
                9.804036E-04, -4.413030E-05,  1.057734E-06,
               -1.052755E-08
            };
            return horner_eval(std::span{d_sub2}, mv);
        } else {
            static constexpr std::array<double, 7> d_sub3 = {
               -1.318058E+02,  4.830222E+01, -1.646031E+00,
                5.464731E-02, -9.650715E-04,  8.802193E-06,
               -3.110810E-08
            };
            return horner_eval(std::span{d_sub3}, mv);
        }
    }

    /* Повний розрахунок з компенсацією холодного спаю */
    [[nodiscard]] static std::expected<double, ThermocoupleError> calculate_temperature(
        double raw_mv, double cj_temp_c, ThermocoupleType type = ThermocoupleType::TypeK) noexcept {
        
        if (cj_temp_c < -50.0 || cj_temp_c > 125.0) {
            return std::unexpected(ThermocoupleError::ColdJunctionOutOfRange);
        }

        if (raw_mv > 65.0 || raw_mv < -10.0) {
            return std::unexpected(ThermocoupleError::SensorBurnout);
        }

        if (type == ThermocoupleType::TypeK) {
            const double v_cj = type_k_temp_to_mv(cj_temp_c);
            const double v_total = raw_mv + v_cj;

            if (v_total < -5.891 || v_total > 54.886) {
                return std::unexpected(ThermocoupleError::VoltageOutOfRange);
            }

            return type_k_mv_to_temp(v_total);
        }

        return std::unexpected(ThermocoupleError::VoltageOutOfRange);
    }
};

} // namespace sensing
