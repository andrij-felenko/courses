// C++20: Інтегральний метод Твейтса та розширений тестовий набір
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <optional>
#include <span>
#include <algorithm>
#include <iomanip>
#include <string_view>

namespace thwaites {

inline constexpr double kLamSep = -0.090;
inline constexpr double kLamMax =  0.250;

[[nodiscard]] constexpr double pow5(double x) noexcept {
    const double x2 = x * x;
    return x2 * x2 * x;
}

[[nodiscard]] constexpr double pow6(double x) noexcept {
    const double x3 = x * x * x;
    return x3 * x3;
}

[[nodiscard]] constexpr double clipLambda(double lam) noexcept {
    return std::clamp(lam, kLamSep, kLamMax);
}

[[nodiscard]] constexpr double shearCorrelation(double lam) noexcept {
    return std::pow(clipLambda(lam) - kLamSep, 0.62);
}

[[nodiscard]] constexpr double shapeCorrelation(double lam) noexcept {
    const double l = clipLambda(lam);
    if (l < 0.0) {
        return 2.088 + 0.0731 / (l + 0.14);
    }
    return 2.61 - 3.75 * l + 5.24 * l * l;
}

struct BoundaryStation {
    double s{0.0};
    double u{0.0};
    double duDs{0.0};
    double theta{0.0};
    double deltaStar{0.0};
    double cf{0.0};
    double lambda{0.0};
    double reTheta{0.0};
};

struct MarchResult {
    std::vector<BoundaryStation> stations;
    std::optional<double> sSeparation;
};

class ThwaitesSolver {
public:
    explicit ThwaitesSolver(double nu = 1.5e-5) noexcept : nu_{nu} {}

    [[nodiscard]] MarchResult solve(std::span<const double> s, 
                                   std::span<const double> u, 
                                   double theta0 = 0.0) const {
        const std::size_t n = s.size();
        MarchResult res;
        res.stations.resize(n);

        // 1. Чисельне диференціювання швидкості dU/ds
        for (std::size_t i = 1; i + 1 < n; ++i) {
            const double h1 = s[i] - s[i - 1];
            const double h2 = s[i + 1] - s[i];
            res.stations[i].duDs = (h1 * h1 * u[i + 1] + (h2 * h2 - h1 * h1) * u[i] - h2 * h2 * u[i - 1]) /
                                   (h1 * h2 * (h1 + h2));
        }
        res.stations.front().duDs = (u[1] - u[0]) / (s[1] - s[0]);
        res.stations.back().duDs  = (u[n - 1] - u[n - 2]) / (s[n - 1] - s[n - 2]);

        // 2. Інтегрування квадратури ∫ U⁵ ds
        std::vector<double> intU5(n, 0.0);
        for (std::size_t i = 1; i < n; ++i) {
            const double avg5 = 0.5 * (pow5(u[i]) + pow5(u[i - 1]));
            intU5[i] = intU5[i - 1] + avg5 * (s[i] - s[i - 1]);
        }

        // 3. Обчислення характеристик примежового шару
        const double seed = theta0 * theta0 * pow6(u.front());
        for (std::size_t i = 0; i < n; ++i) {
            auto& st = res.stations[i];
            st.s = s[i];
            st.u = u[i];

            double th2 = 0.0;
            if (st.u > 1e-6) {
                th2 = (0.45 * nu_ * intU5[i] + seed) / pow6(st.u);
            } else if (st.duDs > 0.0) {
                th2 = 0.075 * nu_ / st.duDs;
            }

            st.theta = std::sqrt(th2);
            st.lambda = (th2 / nu_) * st.duDs;
            st.deltaStar = shapeCorrelation(st.lambda) * st.theta;
            st.cf = (st.u * st.theta > 1e-9) 
                    ? 2.0 * nu_ * shearCorrelation(st.lambda) / (st.u * st.theta) 
                    : 0.0;
            st.reTheta = st.u * st.theta / nu_;
        }

        // 4. Локалізація точки відриву (перший перетин λ = -0.09)
        for (std::size_t i = 1; i < n; ++i) {
            if (res.stations[i].lambda <= kLamSep && res.stations[i - 1].lambda > kLamSep) {
                const double f = (kLamSep - res.stations[i - 1].lambda) / 
                                 (res.stations[i].lambda - res.stations[i - 1].lambda);
                res.sSeparation = res.stations[i - 1].s + f * (res.stations[i].s - res.stations[i - 1].s);
                break;
            }
        }

        return res;
    }

private:
    double nu_;
};

void runTestSuite() {
    const ThwaitesSolver solver(1.5e-5);
    std::cout << std::fixed << std::setprecision(4);

    // Тест 1: Течія Говарта
    {
        constexpr std::size_t n = 201;
        constexpr double l = 1.0, u0 = 20.0;
        std::vector<double> s(n), u(n);
        for (std::size_t i = 0; i < n; ++i) {
            s[i] = 0.15 * l * static_cast<double>(i) / static_cast<double>(n - 1);
            u[i] = u0 * (1.0 - s[i] / l);
        }
        const auto res = solver.solve(s, u);
        std::cout << "[Тест 1] Лінійна течія Говарта:\n";
        if (res.sSeparation) {
            std::cout << "  x_sep / L = " << *res.sSeparation / l 
                      << " (Точне = 0.1198, Відхилення = " 
                      << (*res.sSeparation / l - 0.1198) / 0.1198 * 100.0 << " %)\n\n";
        }
    }

    // Тест 2: Течія Тані
    {
        constexpr std::size_t n = 301;
        constexpr double l = 1.0, u0 = 20.0;
        std::vector<double> s(n), u(n);
        for (std::size_t i = 0; i < n; ++i) {
            s[i] = 0.35 * l * static_cast<double>(i) / static_cast<double>(n - 1);
            const double xi = s[i] / l;
            u[i] = u0 * (1.0 - xi * xi);
        }
        const auto res = solver.solve(s, u);
        std::cout << "[Тест 2] Квадратична течія Тані:\n";
        if (res.sSeparation) {
            std::cout << "  x_sep / L = " << *res.sSeparation / l 
                      << " (Точне = 0.2710, Відхилення = " 
                      << (*res.sSeparation / l - 0.2710) / 0.2710 * 100.0 << " %)\n\n";
        }
    }

    // Тест 3: Обтікання циліндра
    {
        constexpr std::size_t n = 361;
        constexpr double r = 0.5, uInf = 10.0;
        std::vector<double> s(n), u(n);
        for (std::size_t i = 0; i < n; ++i) {
            const double phi = std::numbers::pi * static_cast<double>(i) / static_cast<double>(n - 1);
            s[i] = r * phi;
            u[i] = 2.0 * uInf * std::sin(phi);
        }
        const auto res = solver.solve(s, u);
        std::cout << "[Тест 3] Потенційне обтікання циліндра:\n";
        if (res.sSeparation) {
            const double phiDeg = (*res.sSeparation / r) * 180.0 / std::numbers::pi;
            std::cout << "  phi_sep = " << phiDeg << " deg (Теорія Твейтса = 103.1 deg)\n\n";
        }
    }
}

} // namespace thwaites

int main() {
    std::cout << "=== Чисельне тестування інтегрального методу Твейтса (C++20) ===\n\n";
    thwaites::runTestSuite();
    return 0;
}
