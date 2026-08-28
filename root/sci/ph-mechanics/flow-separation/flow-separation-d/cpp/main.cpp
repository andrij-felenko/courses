// C++20: Інженерний аналіз відриву потоку, примежового шару та вихорів Кармана
#include <iostream>
#include <vector>
#include <cmath>
#include <optional>
#include <span>
#include <algorithm>
#include <iomanip>
#include <numbers>

namespace fluid::separation {

inline constexpr double kThwaitesSepLimit = -0.090;
inline constexpr double kThwaitesMaxLimit =  0.250;

struct StationState {
    double x{0.0};
    double uExt{0.0};
    double duDx{0.0};
    double theta{0.0};
    double deltaStar{0.0};
    double hShape{0.0};
    double lambda{0.0};
    double tauW{0.0};
    double cf{0.0};
    bool isInflection{false};
};

struct VortexSheddingResult {
    double strouhal{0.0};
    double frequencyHz{0.0};
    double liftForceAmpPerMeter{0.0};
    double meanDragForcePerMeter{0.0};
};

struct SeparationResult {
    std::vector<StationState> stations;
    std::optional<double> separationCoordinate;
    std::optional<std::size_t> separationIndex;
};

[[nodiscard]] constexpr double computeThwaitesH(double lambda) noexcept {
    const double l = std::clamp(lambda, kThwaitesSepLimit, kThwaitesMaxLimit);
    if (l < 0.0) {
        return 2.088 + 0.0731 / (l + 0.14);
    }
    return 2.61 - 3.75 * l + 5.24 * l * l;
}

[[nodiscard]] constexpr double computeThwaitesS(double lambda) noexcept {
    const double l = std::clamp(lambda, kThwaitesSepLimit, kThwaitesMaxLimit);
    return std::pow(l + 0.090, 0.62);
}

class BoundaryLayerAnalyzer {
public:
    explicit BoundaryLayerAnalyzer(double rho = 1.225, double nu = 1.5e-5) noexcept
        : rho_{rho}, nu_{nu} {}

    [[nodiscard]] SeparationResult analyze(std::span<const double> x, std::span<const double> u) const {
        const std::size_t n = x.size();
        std::vector<StationState> stations(n);

        std::vector<double> integralU5(n, 0.0);
        for (std::size_t i = 1; i < n; ++i) {
            const double uAvg5 = 0.5 * (std::pow(u[i], 5.0) + std::pow(u[i - 1], 5.0));
            integralU5[i] = integralU5[i - 1] + uAvg5 * (x[i] - x[i - 1]);
        }

        SeparationResult result;

        for (std::size_t i = 0; i < n; ++i) {
            auto& st = stations[i];
            st.x = x[i];
            st.uExt = u[i];

            if (i == 0) {
                st.duDx = (u[1] - u[0]) / (x[1] - x[0]);
            } else if (i == n - 1) {
                st.duDx = (u[n - 1] - u[n - 2]) / (x[n - 1] - x[n - 2]);
            } else {
                const double h1 = x[i] - x[i - 1];
                const double h2 = x[i + 1] - x[i];
                st.duDx = (h1 * h1 * u[i + 1] + (h2 * h2 - h1 * h1) * u[i] - h2 * h2 * u[i - 1]) /
                          (h1 * h2 * (h1 + h2));
            }

            st.isInflection = (st.duDx < 0.0);

            double th2 = 0.0;
            if (u[i] > 1e-5) {
                th2 = (0.45 * nu_ * integralU5[i]) / std::pow(u[i], 6.0);
            } else if (st.duDx > 0.0) {
                th2 = 0.075 * nu_ / st.duDx;
            }

            st.theta = std::sqrt(th2);
            st.lambda = (th2 / nu_) * st.duDx;
            st.hShape = computeThwaitesH(st.lambda);
            st.deltaStar = st.hShape * st.theta;

            const double sVal = computeThwaitesS(st.lambda);
            if (st.theta > 1e-9 && u[i] > 1e-5) {
                st.tauW = (rho_ * nu_ * u[i] / st.theta) * sVal;
                st.cf = 2.0 * st.tauW / (rho_ * u[i] * u[i]);
            } else {
                st.tauW = 0.0;
                st.cf = 0.0;
            }
        }

        for (std::size_t i = 1; i < n; ++i) {
            if (stations[i].lambda <= kThwaitesSepLimit && stations[i - 1].lambda > kThwaitesSepLimit) {
                const double frac = (kThwaitesSepLimit - stations[i - 1].lambda) / 
                                    (stations[i].lambda - stations[i - 1].lambda);
                result.separationCoordinate = stations[i - 1].x + frac * (stations[i].x - stations[i - 1].x);
                result.separationIndex = i;
                break;
            }
        }

        result.stations = std::move(stations);
        return result;
    }

    [[nodiscard]] VortexSheddingResult analyzeKarmanStreet(double uInf, double diameter) const noexcept {
        const double reynolds = uInf * diameter / nu_;
        VortexSheddingResult res;

        if (reynolds < 250.0) {
            res.strouhal = 0.212 * (1.0 - 21.2 / reynolds);
        } else if (reynolds < 2.0e5) {
            res.strouhal = 0.198 * (1.0 - 19.7 / reynolds);
        } else {
            res.strouhal = 0.220;
        }

        res.frequencyHz = res.strouhal * uInf / diameter;

        const double dynamicQ = 0.5 * rho_ * uInf * uInf;
        constexpr double kClAmp = 0.45;
        constexpr double kCdMean = 1.15;

        res.liftForceAmpPerMeter = kClAmp * dynamicQ * diameter;
        res.meanDragForcePerMeter = kCdMean * dynamicQ * diameter;
        return res;
    }

private:
    double rho_;
    double nu_;
};

} // namespace fluid::separation

int main() {
    using namespace fluid::separation;

    constexpr std::size_t kNumPoints = 101;
    constexpr double kLength = 1.0;
    constexpr double kU0 = 25.0;
    constexpr double kRho = 1.225;
    constexpr double kNu = 1.5e-5;

    std::vector<double> x(kNumPoints);
    std::vector<double> u(kNumPoints);

    for (std::size_t i = 0; i < kNumPoints; ++i) {
        x[i] = static_cast<double>(i) / static_cast<double>(kNumPoints - 1) * 0.35 * kLength;
        u[i] = kU0 * (1.0 - 0.5 * (x[i] / kLength));
    }

    const BoundaryLayerAnalyzer analyzer(kRho, kNu);
    const SeparationResult result = analyzer.analyze(x, u);

    std::cout << "=== Інженерний аналіз відриву примежового шару (C++20) ===\n";
    std::cout << "U_0 = " << kU0 << " м/с, L = " << kLength << " м, ν = " << kNu << " м²/с\n\n";

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "  x, м      U(x), м/с   θ, мм     H        λ        τ_w, Па   Перегин\n";
    std::cout << "------------------------------------------------------------------\n";
    for (std::size_t i = 0; i < kNumPoints; i += 15) {
        const auto& st = result.stations[i];
        std::cout << "  " << st.x << "    "
                  << std::setw(8) << std::setprecision(2) << st.uExt << "   "
                  << std::setw(7) << std::setprecision(4) << st.theta * 1000.0 << "   "
                  << std::setw(6) << std::setprecision(3) << st.hShape << "   "
                  << std::setw(7) << std::setprecision(4) << st.lambda << "   "
                  << std::setw(8) << std::setprecision(4) << st.tauW << "   "
                  << (st.isInflection ? "ТАК" : "НІ") << "\n";
    }
    std::cout << "------------------------------------------------------------------\n";

    if (result.separationCoordinate) {
        std::cout << "ТОЧКА ВІДРИВУ ПОТОКУ: x_sep = " << *result.separationCoordinate 
                  << " м (x/L = " << *result.separationCoordinate / kLength << ")\n\n";
    }

    constexpr double kDiameter = 0.15;
    const VortexSheddingResult vs = analyzer.analyzeKarmanStreet(kU0, kDiameter);

    std::cout << "=== Характеристики вихрової доріжки фон Кармана ===\n";
    std::cout << "Тіло: циліндр D = " << kDiameter << " м, Re = " << kU0 * kDiameter / kNu << "\n";
    std::cout << "Число Струхаля St = " << vs.strouhal << "\n";
    std::cout << "Частота зриву вихорів f = " << vs.frequencyHz << " Гц\n";
    std::cout << "Амплітуда бічної сили F_y = " << vs.liftForceAmpPerMeter << " Н/м\n";
    std::cout << "Середній опір тиску F_x = " << vs.meanDragForcePerMeter << " Н/м\n";

    return 0;
}
