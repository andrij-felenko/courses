// C++20: Модуль розрахунку примежового шару методом Твейтса на профілях NACA
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <optional>
#include <span>
#include <algorithm>
#include <iomanip>
#include <string_view>

namespace airfoil::thwaites {

inline constexpr double kLamSep = -0.090;
inline constexpr double kLamMax =  0.250;

struct AirfoilGeometry {
    double maxCamber{0.02};       // m: максимальний кембер (NACA 2412)
    double camberLoc{0.4};        // p: положення кембера
    double maxThickness{0.12};    // t: відносна товщина
    double chord{1.0};            // c: довжина хорди, м
};

struct BoundaryPoint {
    double x{0.0};          // хордова координата, м
    double y{0.0};          // вертикальна координата спинки, м
    double s{0.0};          // довжина дуги від носка, м
    double uExt{0.0};       // зовнішня швидкість U(s), м/с
    double duDs{0.0};       // поздовжній градієнт dU/ds, 1/с
    double theta{0.0};      // товщина втрати імпульсу θ, м
    double deltaStar{0.0};  // товщина витіснення δ*, м
    double hShape{0.0};     // форм-параметр H = δ*/θ
    double lambda{0.0};     // параметр Твейтса λ
    double cf{0.0};         // коефіцієнт тертя c_f
    double reTheta{0.0};    // число Рейнольдса Re_θ
    
    // Параметри за методом Польгаузена
    double deltaPohl{0.0};  // товщина шару δ
    double lambdaPohl{0.0}; // форм-параметр Λ
    double cfPohl{0.0};     // коефіцієнт тертя
};

struct SolverOutput {
    std::vector<BoundaryPoint> stations;
    std::optional<double> xSeparation;
    std::optional<double> sSeparation;
    std::optional<double> xPohlSeparation;
    std::optional<double> sTransition;
};

[[nodiscard]] constexpr double shearCorrelation(double lam) noexcept {
    const double lClip = std::clamp(lam, kLamSep, kLamMax);
    return std::pow(lClip - kLamSep, 0.62);
}

[[nodiscard]] constexpr double shapeCorrelation(double lam) noexcept {
    const double lClip = std::clamp(lam, kLamSep, kLamMax);
    if (lClip < 0.0) {
        return 2.088 + 0.0731 / (lClip + 0.14);
    }
    return 2.61 - 3.75 * lClip + 5.24 * lClip * lClip;
}

[[nodiscard]] inline double michelTransitionCriterion(double reS) noexcept {
    if (reS < 100.0) return 1e9;
    return 1.174 * (1.0 + 22400.0 / reS) * std::pow(reS, 0.46);
}

class AirfoilBoundaryLayerSolver {
public:
    explicit AirfoilBoundaryLayerSolver(AirfoilGeometry geom, double nu = 1.5e-5) noexcept
        : geom_{geom}, nu_{nu} {}

    [[nodiscard]] SolverOutput solve(double alphaDeg, double uInf, std::size_t numPoints = 161) const {
        const double alphaRad = alphaDeg * std::numbers::pi / 180.0;
        std::vector<BoundaryPoint> pts(numPoints);

        // 1. Побудова координат та розподілу швидкості
        for (std::size_t i = 0; i < numPoints; ++i) {
            const double beta = std::numbers::pi * static_cast<double>(i) / static_cast<double>(numPoints - 1);
            const double xc = 0.5 * (1.0 - std::cos(beta));

            double yc = 0.0;
            double dycDx = 0.0;
            if (geom_.maxCamber > 0.0 && geom_.camberLoc > 0.0) {
                if (xc < geom_.camberLoc) {
                    yc = (geom_.maxCamber / (geom_.camberLoc * geom_.camberLoc)) * (2.0 * geom_.camberLoc * xc - xc * xc);
                    dycDx = (2.0 * geom_.maxCamber / (geom_.camberLoc * geom_.camberLoc)) * (geom_.camberLoc - xc);
                } else {
                    const double p1 = 1.0 - geom_.camberLoc;
                    yc = (geom_.maxCamber / (p1 * p1)) * ((1.0 - 2.0 * geom_.camberLoc) + 2.0 * geom_.camberLoc * xc - xc * xc);
                    dycDx = (2.0 * geom_.maxCamber / (p1 * p1)) * (geom_.camberLoc - xc);
                }
            }
            const double thetaC = std::atan(dycDx);
            const double yt = 5.0 * geom_.maxThickness * (0.2969 * std::sqrt(xc) - 0.1260 * xc - 
                                                         0.3516 * xc * xc + 0.2843 * xc * xc * xc - 
                                                         0.1015 * xc * xc * xc * xc);

            pts[i].x = (xc - yt * std::sin(thetaC)) * geom_.chord;
            pts[i].y = (yc + yt * std::cos(thetaC)) * geom_.chord;

            if (xc < 1e-6) {
                pts[i].uExt = 0.0;
            } else {
                const double thicknessFactor = 1.0 + 1.2 * geom_.maxThickness * (1.0 - xc);
                const double camberFactor = 1.0 + 2.5 * geom_.maxCamber * std::sin(std::numbers::pi * xc);
                const double alphaLift = 2.0 * std::sin(alphaRad + 2.0 * geom_.maxCamber) * std::sqrt((1.0 - xc) / (xc + 0.005));
                const double vRatio = std::max(0.0, std::cos(alphaRad) * thicknessFactor * camberFactor + alphaLift);
                pts[i].uExt = uInf * vRatio;
            }
        }

        // Розрахунок довжини дуги s
        pts[0].s = 0.0;
        for (std::size_t i = 1; i < numPoints; ++i) {
            const double dx = pts[i].x - pts[i - 1].x;
            const double dy = pts[i].y - pts[i - 1].y;
            pts[i].s = pts[i - 1].s + std::hypot(dx, dy);
        }

        // 2. Обчислення градієнта швидкості dU/ds
        for (std::size_t i = 1; i + 1 < numPoints; ++i) {
            const double h1 = pts[i].s - pts[i - 1].s;
            const double h2 = pts[i + 1].s - pts[i].s;
            pts[i].duDs = (h1 * h1 * pts[i + 1].uExt + (h2 * h2 - h1 * h1) * pts[i].uExt - h2 * h2 * pts[i - 1].uExt) /
                          (h1 * h2 * (h1 + h2));
        }
        pts.front().duDs = (pts[1].uExt - pts[0].uExt) / (pts[1].s - pts[0].s);
        pts.back().duDs  = (pts.back().uExt - pts[numPoints - 2].uExt) / (pts.back().s - pts[numPoints - 2].s);

        // 3. Інтегрування квадратури ∫ U⁵ ds
        std::vector<double> intU5(numPoints, 0.0);
        for (std::size_t i = 1; i < numPoints; ++i) {
            const double uAvg5 = 0.5 * (std::pow(pts[i].uExt, 5.0) + std::pow(pts[i - 1].uExt, 5.0));
            intU5[i] = intU5[i - 1] + uAvg5 * (pts[i].s - pts[i - 1].s);
        }

        SolverOutput out;
        out.stations = std::move(pts);

        // 4. Розрахунок параметрів Твейтса та Польгаузена
        for (std::size_t i = 0; i < numPoints; ++i) {
            auto& pt = out.stations[i];
            double th2 = 0.0;
            if (pt.uExt > 1e-4) {
                th2 = (0.45 * nu_ * intU5[i]) / std::pow(pt.uExt, 6.0);
            } else if (pt.duDs > 0.0) {
                th2 = 0.075 * nu_ / pt.duDs;
            }

            pt.theta = std::sqrt(th2);
            pt.lambda = (th2 / nu_) * pt.duDs;
            pt.hShape = shapeCorrelation(pt.lambda);
            pt.deltaStar = pt.hShape * pt.theta;
            pt.cf = (pt.uExt * pt.theta > 1e-9) ? 2.0 * nu_ * shearCorrelation(pt.lambda) / (pt.uExt * pt.theta) : 0.0;
            pt.reTheta = pt.uExt * pt.theta / nu_;

            // Польгаузен
            pt.deltaPohl = pt.theta / 0.11746;
            pt.lambdaPohl = (pt.deltaPohl * pt.deltaPohl / nu_) * pt.duDs;
            const double pohlFactor = std::max(0.0, 2.0 + pt.lambdaPohl / 6.0);
            pt.cfPohl = (pt.uExt * pt.deltaPohl > 1e-9) ? 2.0 * (nu_ / (pt.uExt * pt.deltaPohl)) * pohlFactor : 0.0;

            if (!out.sTransition && i > 0) {
                const double reS = pt.uExt * pt.s / nu_;
                if (pt.reTheta >= michelTransitionCriterion(reS)) {
                    out.sTransition = pt.s;
                }
            }
        }

        // Локалізація Твейтса
        for (std::size_t i = 1; i < numPoints; ++i) {
            if (out.stations[i].lambda <= kLamSep && out.stations[i - 1].lambda > kLamSep) {
                const double factor = (kLamSep - out.stations[i - 1].lambda) / 
                                      (out.stations[i].lambda - out.stations[i - 1].lambda);
                out.sSeparation = out.stations[i - 1].s + factor * (out.stations[i].s - out.stations[i - 1].s);
                out.xSeparation = out.stations[i - 1].x + factor * (out.stations[i].x - out.stations[i - 1].x);
                break;
            }
        }

        // Локалізація Польгаузена (Λ = -12.0)
        for (std::size_t i = 1; i < numPoints; ++i) {
            if (out.stations[i].lambdaPohl <= -12.0 && out.stations[i - 1].lambdaPohl > -12.0) {
                const double factor = (-12.0 - out.stations[i - 1].lambdaPohl) / 
                                      (out.stations[i].lambdaPohl - out.stations[i - 1].lambdaPohl);
                out.xPohlSeparation = out.stations[i - 1].x + factor * (out.stations[i].x - out.stations[i - 1].x);
                break;
            }
        }

        return out;
    }

private:
    AirfoilGeometry geom_;
    double nu_;
};

void runAirfoilTestSuite() {
    constexpr double nu = 1.5e-5;
    constexpr double uInf = 30.0;
    
    const std::vector<std::pair<std::string_view, AirfoilGeometry>> foils = {
        { "NACA 0012", { .maxCamber = 0.00, .camberLoc = 0.0, .maxThickness = 0.12, .chord = 1.0 } },
        { "NACA 2412", { .maxCamber = 0.02, .camberLoc = 0.4, .maxThickness = 0.12, .chord = 1.0 } },
        { "NACA 4412", { .maxCamber = 0.04, .camberLoc = 0.4, .maxThickness = 0.12, .chord = 1.0 } }
    };
    const std::vector<double> alphas = { 0.0, 4.0, 8.0 };

    std::cout << "\n=== Зведена таблиця розрахунків Твейтса для профілів NACA (C++20) ===\n";
    std::cout << std::left << std::setw(11) << "Профіль" 
              << std::setw(8) << "Alpha" 
              << std::setw(14) << "x_sep/c(Thw)" 
              << std::setw(14) << "x_sep/c(Pohl)" 
              << std::setw(12) << "θ_sep, мм" 
              << std::setw(12) << "Re_θ,sep\n";
    std::cout << "-------------------------------------------------------------------------\n";

    for (const auto& [name, geom] : foils) {
        AirfoilBoundaryLayerSolver solver(geom, nu);
        for (double alpha : alphas) {
            const auto res = solver.solve(alpha, uInf, 161);
            const double xThw = res.xSeparation ? (*res.xSeparation / geom.chord) : 1.0;
            const double xPoh = res.xPohlSeparation ? (*res.xPohlSeparation / geom.chord) : 1.0;
            
            double thSep = 0.0, reTh = 0.0;
            if (res.xSeparation) {
                for (const auto& st : res.stations) {
                    if (st.x >= *res.xSeparation) {
                        thSep = st.theta * 1000.0;
                        reTh = st.reTheta;
                        break;
                    }
                }
            }

            std::cout << std::left << std::setw(11) << name 
                      << std::fixed << std::setprecision(1) << std::setw(8) << alpha 
                      << std::fixed << std::setprecision(4) << std::setw(14) << xThw 
                      << std::fixed << std::setprecision(4) << std::setw(14) << xPoh 
                      << std::fixed << std::setprecision(4) << std::setw(12) << thSep 
                      << std::fixed << std::setprecision(1) << std::setw(12) << reTh << "\n";
        }
    }
    std::cout << "-------------------------------------------------------------------------\n\n";
}

} // namespace airfoil::thwaites

int main() {
    using namespace airfoil::thwaites;

    const AirfoilGeometry naca2412{ .maxCamber = 0.02, .camberLoc = 0.4, .maxThickness = 0.12, .chord = 1.0 };
    const double uInf = 30.0;
    const double nu = 1.5e-5;
    const double alpha = 4.0;

    const AirfoilBoundaryLayerSolver solver(naca2412, nu);
    const SolverOutput res = solver.solve(alpha, uInf, 161);

    std::cout << "=== Розрахунок примежового шару методом Твейтса (C++20) ===\n";
    std::cout << "Профіль: NACA 2412, c = " << naca2412.chord << " м, U_inf = " << uInf << " м/с, Alpha = " << alpha << " deg\n\n";

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "  x/c      s/c      U [м/с]   θ [мм]    H        λ        cf·10³    Re_θ\n";
    std::cout << "-------------------------------------------------------------------------\n";

    const std::size_t step = res.stations.size() / 16;
    for (std::size_t i = 0; i < res.stations.size(); i += step) {
        const auto& pt = res.stations[i];
        std::cout << "  " << pt.x / naca2412.chord << "   " << pt.s / naca2412.chord << "   "
                  << std::setw(7) << std::setprecision(2) << pt.uExt << "   "
                  << std::setw(7) << std::setprecision(4) << pt.theta * 1000.0 << "   "
                  << std::setw(6) << std::setprecision(3) << pt.hShape << "   "
                  << std::setw(7) << std::setprecision(4) << pt.lambda << "   "
                  << std::setw(7) << std::setprecision(4) << pt.cf * 1000.0 << "   "
                  << std::setw(7) << std::setprecision(1) << pt.reTheta << "\n";
    }
    std::cout << "-------------------------------------------------------------------------\n";

    if (res.xSeparation) {
        std::cout << "Ламінарний відрив (Твейтс):    x_sep/c = " << *res.xSeparation / naca2412.chord 
                  << " (s_sep = " << *res.sSeparation << " м)\n";
    }
    if (res.xPohlSeparation) {
        std::cout << "Ламінарний відрив (Польгаузен): x_sep/c = " << *res.xPohlSeparation / naca2412.chord 
                  << " (Λ = -12.0)\n";
    }
    if (res.sTransition) {
        std::cout << "Перехід Мішеля Re_θ ≥ Re_θ,tr: s_tr = " << *res.sTransition << " м\n";
    }

    runAirfoilTestSuite();
    return 0;
}
