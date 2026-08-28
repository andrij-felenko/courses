// henon_sim.cpp — Ідіоматична реалізація відображення Ено мовою C++20
#include <iostream>
#include <vector>
#include <cmath>
#include <array>
#include <fstream>
#include <expected>
#include <string>

namespace henon {

struct Params {
    double a{1.4};
    double b{0.3};
};

struct Point {
    double x{0.0};
    double y{0.0};
};

enum class SimError {
    DivergedToInfinity,
    InvalidSteps
};

class Model {
public:
    explicit Model(Params params) : params_(params) {}

    [[nodiscard]] Point step(Point current) const noexcept {
        return Point{
            .x = 1.0 - params_.a * current.x * current.x + current.y,
            .y = params_.b * current.x
        };
    }

    [[nodiscard]] std::expected<std::vector<Point>, SimError> generate_orbit(
        Point start, std::size_t transient, std::size_t count) const {
        
        Point pt = start;
        for (std::size_t i = 0; i < transient; ++i) {
            pt = step(pt);
            if (std::abs(pt.x) > 1e4) {
                return std::unexpected(SimError::DivergedToInfinity);
            }
        }

        std::vector<Point> orbit;
        orbit.reserve(count);
        for (std::size_t i = 0; i < count; ++i) {
            pt = step(pt);
            if (std::abs(pt.x) > 1e4) {
                return std::unexpected(SimError::DivergedToInfinity);
            }
            orbit.push_back(pt);
        }
        return orbit;
    }

    [[nodiscard]] std::expected<double, SimError> compute_lyapunov(
        Point start, std::size_t transient, std::size_t steps) const {
        
        Point pt = start;
        for (std::size_t i = 0; i < transient; ++i) {
            pt = step(pt);
            if (std::abs(pt.x) > 1e4) {
                return std::unexpected(SimError::DivergedToInfinity);
            }
        }

        std::array<double, 2> tangent{1.0, 0.0};
        double log_sum = 0.0;

        for (std::size_t i = 0; i < steps; ++i) {
            double next_dx = -2.0 * params_.a * pt.x * tangent[0] + tangent[1];
            double next_dy = params_.b * tangent[0];

            double norm = std::hypot(next_dx, next_dy);
            if (norm < 1e-12) break;

            log_sum += std::log(norm);
            tangent = {next_dx / norm, next_dy / norm};
            pt = step(pt);
        }

        return log_sum / static_cast<double>(steps);
    }

private:
    Params params_;
};

} // namespace henon

int main() {
    henon::Params params{.a = 1.4, .b = 0.3};
    henon::Model model(params);

    auto result = model.compute_lyapunov({0.1, 0.1}, 1000, 100000);
    if (result) {
        std::cout << "Показник Ляпунова (C++): lambda_1 = " << *result << '\n';
    } else {
        std::cerr << "Помилка обчислення: траєкторія розбіглася\n";
    }

    return 0;
}
