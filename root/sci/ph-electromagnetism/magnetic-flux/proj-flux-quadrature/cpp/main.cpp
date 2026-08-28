#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <span>
#include <expected>
#include <numeric>
#include <execution>

struct Wire2D {
    double x{0.0};
    double y{0.0};
    double current{0.0};
};

struct GridBounds {
    double x_min{0.0}, x_max{0.0};
    double y_min{0.0}, y_max{0.0};
    std::size_t nx{100}, ny{100};
};

enum class IntegrationError {
    InvalidBounds,
    ZeroMeshSteps,
    NullPointerData
};

class FluxIntegrator2D {
public:
    static constexpr double mu_0 = 4.0 * std::numbers::pi * 1e-7;

    [[nodiscard]] static double compute_bz(double x, double y, std::span<const Wire2D> wires) noexcept {
        double bz_total = 0.0;
        for (const auto& wire : wires) {
            const double dx = x - wire.x;
            const double dy = y - wire.y;
            double r2 = dx * dx + dy * dy;
            if (r2 < 1e-12) {
                r2 = 1e-12;
            }
            const double b_mag = (mu_0 * wire.current) / (2.0 * std::numbers::pi * r2);
            bz_total += b_mag * dx;
        }
        return bz_total;
    }

    [[nodiscard]] static std::expected<double, IntegrationError> 
    calculate_flux(const GridBounds& bounds, std::span<const Wire2D> wires) noexcept {
        if (bounds.nx == 0 || bounds.ny == 0) {
            return std::unexpected(IntegrationError::ZeroMeshSteps);
        }
        if (bounds.x_max <= bounds.x_min || bounds.y_max <= bounds.y_min) {
            return std::unexpected(IntegrationError::InvalidBounds);
        }

        const double dx = (bounds.x_max - bounds.x_min) / static_cast<double>(bounds.nx);
        const double dy = (bounds.y_max - bounds.y_min) / static_cast<double>(bounds.ny);

        std::vector<std::size_t> indices(bounds.nx + 1);
        std::iota(indices.begin(), indices.end(), 0);

        // Паралельне обчислення рядків сітки
        const double total_sum = std::transform_reduce(
            std::execution::par,
            indices.begin(), indices.end(),
            0.0,
            std::plus<>(),
            [&](std::size_t i) {
                const double x = bounds.x_min + static_cast<double>(i) * dx;
                const double weight_x = (i == 0 || i == bounds.nx) ? 0.5 : 1.0;
                double row_sum = 0.0;

                for (std::size_t j = 0; j <= bounds.ny; ++j) {
                    const double y = bounds.y_min + static_cast<double>(j) * dy;
                    const double weight_y = (j == 0 || j == bounds.ny) ? 0.5 : 1.0;
                    row_sum += weight_x * weight_y * compute_bz(x, y, wires);
                }
                return row_sum;
            }
        );

        return total_sum * dx * dy;
    }
};

int main() {
    const std::vector<Wire2D> wires = {
        { .x = 0.0, .y = 0.0, .current = 10.0 }
    };

    const GridBounds bounds = {
        .x_min = 0.01, .x_max = 0.05,
        .y_min = 0.00, .y_max = 0.10,
        .nx = 200, .ny = 200
    };

    const auto result = FluxIntegrator2D::calculate_flux(bounds, wires);

    if (result.has_value()) {
        const double flux = result.value();
        std::cout << "C++23 Чисельний потік: " << flux << " Wb\n";

        const double flux_exact = (FluxIntegrator2D::mu_0 * 10.0 * 0.10 / 
                                  (2.0 * std::numbers::pi)) * std::log(0.05 / 0.01);
        std::cout << "Аналітичний потік:    " << flux_exact << " Wb\n";
        std::cout << "Відносна похибка:      " 
                  << std::abs((flux - flux_exact) / flux_exact) * 100.0 << "%\n";
    } else {
        std::cerr << "Помилка чисельного інтегрування!\n";
        return 1;
    }

    return 0;
}
