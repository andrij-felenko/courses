#include <iostream>
#include <vector>
#include <cmath>
#include <optional>
#include <span>
#include <memory>
#include <expected>
#include <string_view>

struct Point2D {
    double x{0.0};
    double y{0.0};
};

struct HorseshoeParams {
    double alpha{0.35};
    double beta{2.4};
};

enum class MappingError {
    OutOfBounds,
    EscapedDomain
};

class SmaleHorseshoeMap {
public:
    explicit SmaleHorseshoeMap(HorseshoeParams params) : params_(params) {}

    [[nodiscard]] std::expected<Point2D, MappingError> forward(const Point2D& p) const {
        if (p.x < 0.0 || p.x > 1.0 || p.y < 0.0 || p.y > 1.0) {
            return std::unexpected(MappingError::OutOfBounds);
        }

        if (p.y >= 0.0 && p.y <= params_.alpha) {
            return Point2D{params_.alpha * p.x, params_.beta * p.y};
        }
        if (p.y >= (1.0 - params_.alpha) && p.y <= 1.0) {
            return Point2D{1.0 - params_.alpha * p.x, params_.beta * (1.0 - p.y)};
        }

        return std::unexpected(MappingError::EscapedDomain);
    }

    [[nodiscard]] std::expected<Point2D, MappingError> inverse(const Point2D& p) const {
        if (p.x < 0.0 || p.x > 1.0 || p.y < 0.0 || p.y > 1.0) {
            return std::unexpected(MappingError::OutOfBounds);
        }

        if (p.x >= 0.0 && p.x <= params_.alpha) {
            return Point2D{p.x / params_.alpha, p.y / params_.beta};
        }
        if (p.x >= (1.0 - params_.alpha) && p.x <= 1.0) {
            return Point2D{(1.0 - p.x) / params_.alpha, 1.0 - (p.y / params_.beta)};
        }

        return std::unexpected(MappingError::EscapedDomain);
    }

    [[nodiscard]] std::pair<double, double> lyapunovExponents() const noexcept {
        return {std::log(params_.alpha), std::log(params_.beta)};
    }

    [[nodiscard]] Point2D reconstructFromSymbolicCode(std::span<const int> code_future,
                                                      std::span<const int> code_past) const {
        double x = 0.0;
        double alpha_power = 1.0;
        for (int s : code_future) {
            if (s == 1) {
                x += alpha_power * (1.0 - params_.alpha);
            }
            alpha_power *= params_.alpha;
        }

        double y = 0.0;
        double beta_power = 1.0 / params_.beta;
        for (int s : code_past) {
            if (s == 1) {
                y += beta_power;
            }
            beta_power /= params_.beta;
        }

        return Point2D{x, y};
    }

private:
    HorseshoeParams params_;
};

int main() {
    HorseshoeParams params{.alpha = 0.35, .beta = 2.4};
    SmaleHorseshoeMap map(params);

    std::cout << "--- Симуляція відображення підкови Смейла (C++) ---\n";
    auto [lx, ly] = map.lyapunovExponents();
    std::cout << "Показники Ляпунова: lambda_x = " << lx << ", lambda_y = " << ly << "\n";

    Point2D p{.x = 0.4, .y = 0.2};
    auto result = map.forward(p);
    if (result) {
        std::cout << "Пряме відображення (0.4, 0.2) -> ("
                  << result->x << ", " << result->y << ")\n";
    } else {
        std::cout << "Точка вилетіла за межі квадрата S\n";
    }

    std::vector<int> future_code{0, 1, 0, 1, 1};
    std::vector<int> past_code{1, 0, 1};
    Point2D reconstructed = map.reconstructFromSymbolicCode(future_code, past_code);
    std::cout << "Відновлені координати з коду: x = " << reconstructed.x
              << ", y = " << reconstructed.y << "\n";

    return 0;
}
