#include <iostream>
#include <vector>
#include <cmath>
#include <span>

class FractalAnalyzer {
public:
    static double computeCapacityDimension(double alpha, double beta) noexcept {
        const double d_x = std::log(2.0) / std::log(1.0 / alpha);
        const double d_y = std::log(2.0) / std::log(beta);
        return d_x + d_y;
    }

    static std::vector<Point2D> generatePeriodicOrbitSet(std::span<const int> period_code,
                                                          const SmaleHorseshoeMap& map) {
        std::vector<Point2D> orbit;
        orbit.reserve(period_code.size());

        Point2D start_p = map.reconstructFromSymbolicCode(period_code, period_code);
        Point2D current = start_p;

        for (size_t i = 0; i < period_code.size(); ++i) {
            orbit.push_back(current);
            auto next_res = map.forward(current);
            if (next_res) {
                current = *next_res;
            } else {
                break;
            }
        }
        return orbit;
    }
};
