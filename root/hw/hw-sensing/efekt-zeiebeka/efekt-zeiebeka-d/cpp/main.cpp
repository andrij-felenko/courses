#include <array>
#include <numeric>
#include <span>

namespace sensors {

class ThermocoupleLinearizer {
public:
    static constexpr std::array<double, 10> k_inv_poly{
         0.0000000E+00,
         2.5083550E+01,
         7.8601060E-02,
        -2.5031310E-01,
         8.3152700E-02,
        -1.2280340E-02,
         9.8040360E-04,
        -4.4130300E-05,
         1.0577340E-06,
        -1.0527550E-08
    };

    [[nodiscard]] static constexpr double cjc_equivalent_uv(double ambient_temp_c) noexcept {
        return ambient_temp_c * 40.73;
    }

    [[nodiscard]] static constexpr double calculate_temperature(double measured_uv, double ambient_temp_c) noexcept {
        const double v_total_mv = (measured_uv + cjc_equivalent_uv(ambient_temp_c)) * 1e-3;

        // Обчислення полінома за схемою Горнера
        double temp = k_inv_poly.back();
        for (auto it = k_inv_poly.rbegin() + 1; it != k_inv_poly.rend(); ++it) {
            temp = temp * v_total_mv + *it;
        }
        return temp;
    }
};

} // namespace sensors
