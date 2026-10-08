#include <iostream>
#include <cmath>

class PlatinumRTD {
public:
    static constexpr double A = 3.9083e-3;
    static constexpr double B = -5.775e-7;
    static constexpr double C = -4.183e-12;

    explicit PlatinumRTD(double r0 = 100.0) : r0_(r0) {}

    [[nodiscard]] double calculateResistance(double t) const noexcept {
        if (t >= 0.0) {
            return r0_ * (1.0 + A * t + B * t * t);
        }
        const double tMinus100 = t - 100.0;
        const double tCubed = t * t * t;
        return r0_ * (1.0 + A * t + B * t * t + C * tMinus100 * tCubed);
    }

private:
    double r0_;
};
