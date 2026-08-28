#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <optional>
#include <string>

struct RayResult {
    double y0;
    double z_surf;
    double z_focus;
    double ds_prime;
    double u_prime_deg;
};

class SphericalSurfaceTracer {
private:
    double R;
    double n1;
    double n2;
    double z_paraxial;

public:
    SphericalSurfaceTracer(double radius, double index1, double index2)
        : R(radius), n1(index1), n2(index2), 
          z_paraxial((index2 * radius) / (index2 - index1)) {}

    [[nodiscard]] double get_paraxial_focus() const noexcept {
        return z_paraxial;
    }

    [[nodiscard]] std::optional<RayResult> trace_ray(double y0) const noexcept {
        if (std::abs(y0) >= std::abs(R)) {
            return std::nullopt;
        }

        const double z_surf = R - std::sqrt(R * R - y0 * y0);
        const double sin_alpha = y0 / R;
        const double sin_theta2 = (n1 / n2) * sin_alpha;

        if (std::abs(sin_theta2) > 1.0) {
            return std::nullopt;
        }

        const double alpha = std::asin(sin_alpha);
        const double theta2 = std::asin(sin_theta2);
        const double u_prime = alpha - theta2;

        const double z_focus = (std::abs(u_prime) < 1e-12) 
            ? z_paraxial 
            : z_surf + y0 / std::tan(u_prime);

        return RayResult{
            y0,
            z_surf,
            z_focus,
            z_focus - z_paraxial,
            u_prime * (180.0 / M_PI)
        };
    }
};

int main() {
    SphericalSurfaceTracer tracer(100.0, 1.0, 1.5);
    std::cout << "Параксіальний фокус z_p = " << std::fixed << std::setprecision(4)
              << tracer.get_paraxial_focus() << " мм\n\n";

    std::cout << std::setw(8) << "y0 (мм)" << " | "
              << std::setw(11) << "z_surf (мм)" << " | "
              << std::setw(12) << "z_focus (мм)" << " | "
              << std::setw(10) << "ds_prime" << " | "
              << std::setw(10) << "U' (град)" << "\n";
    std::cout << std::string(64, '-') << "\n";

    const std::vector<double> heights = {5.0, 10.0, 20.0, 30.0, 40.0, 50.0};
    for (double y : heights) {
        if (auto res = tracer.trace_ray(y)) {
            std::cout << std::setw(8) << std::setprecision(1) << res->y0 << " | "
                      << std::setw(11) << std::setprecision(4) << res->z_surf << " | "
                      << std::setw(12) << std::setprecision(4) << res->z_focus << " | "
                      << std::setw(10) << std::setprecision(4) << res->u_prime_deg << "\n";
        }
    }
    return 0;
}
