#include <iostream>
#include <complex>
#include <cmath>
#include <vector>
#include <iomanip>

namespace Optics {

constexpr double PI = 3.14159265358979323846;

// Вектор поляризації Джонса (Ex, Ey)
class JonesVector {
public:
    using Complex = std::complex<double>;

    Complex ex{1.0, 0.0};
    Complex ey{0.0, 0.0};

    constexpr JonesVector() = default;
    constexpr JonesVector(Complex x, Complex y) : ex(x), ey(y) {}

    [[nodiscard]] double intensity() const noexcept {
        return std::norm(ex) + std::norm(ey);
    }
};

// Матриця оптичного елемента 2x2
class JonesMatrix {
public:
    using Complex = std::complex<double>;

    Complex m00{1, 0}, m01{0, 0};
    Complex m10{0, 0}, m11{1, 0};

    constexpr JonesMatrix() = default;
    constexpr JonesMatrix(Complex c00, Complex c01, Complex c10, Complex c11)
        : m00(c00), m01(c01), m10(c10), m11(c11) {}

    [[nodiscard]] JonesVector operator*(const JonesVector& v) const noexcept {
        return JonesVector(
            m00 * v.ex + m01 * v.ey,
            m10 * v.ex + m11 * v.ey
        );
    }

    // Лінійний поляризатор під кутом alpha
    static JonesMatrix createPolarizer(double alphaRad) {
        const double c = std::cos(alphaRad);
        const double s = std::sin(alphaRad);
        return JonesMatrix(c * c, c * s, c * s, s * s);
    }

    // Нереципрокний ротатор Фарадея
    static JonesMatrix createFaradayRotator(double thetaRad, bool isForward) {
        const double sign = isForward ? 1.0 : -1.0;
        const double rot = sign * thetaRad;
        const double c = std::cos(rot);
        const double s = std::sin(rot);
        return JonesMatrix(c, -s, s, c);
    }
};

// Симулятор оптичного ізолятора
class FaradayIsolatorSimulator {
private:
    double rotationAngleRad_;

public:
    explicit FaradayIsolatorSimulator(double rotationAngleDeg = 45.0)
        : rotationAngleRad_(rotationAngleDeg * PI / 180.0) {}

    struct SimulationResult {
        double insertionLossDb;
        double isolationDb;
        double forwardEfficiency;
        double backwardLeakage;
    };

    [[nodiscard]] SimulationResult runSimulation(double angleErrorDeg = 0.0) const {
        const double actualRotRad = rotationAngleRad_ - (angleErrorDeg * PI / 180.0);

        const auto P1 = JonesMatrix::createPolarizer(0.0);
        const auto P2 = JonesMatrix::createPolarizer(PI / 4.0); // 45 градусів
        const auto FR_fwd = JonesMatrix::createFaradayRotator(actualRotRad, true);
        const auto FR_bwd = JonesMatrix::createFaradayRotator(actualRotRad, false);

        // Прямий хід
        const JonesVector E_in{1.0, 0.0};
        const JonesVector E_fwd = P2 * (FR_fwd * (P1 * E_in));
        const double I_fwd = E_fwd.intensity();
        const double I_in = E_in.intensity();

        // Зворотний хід
        const JonesVector E_back_in{std::cos(PI / 4.0), std::sin(PI / 4.0)};
        const JonesVector E_bwd = P1 * (FR_bwd * (P2 * E_back_in));
        const double I_bwd = E_bwd.intensity();
        const double I_back_in = E_back_in.intensity();

        const double insLoss = -10.0 * std::log10(I_fwd / I_in);
        const double iso = (I_bwd < 1e-12) ? 120.0 : -10.0 * std::log10(I_bwd / I_back_in);

        return SimulationResult{ insLoss, iso, I_fwd / I_in, I_bwd / I_back_in };
    }
};

} // namespace Optics

int main() {
    std::cout << "=== C++17 Оптичний ізолятор Фарадея ===\n\n";

    Optics::FaradayIsolatorSimulator isolator(45.0);
    auto baseRes = isolator.runSimulation(0.0);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Ідеальний ізолятор (θ = 45.0°):\n";
    std::cout << "  - Втрати на вставку (Insertion Loss): " << baseRes.insertionLossDb << " дБ\n";
    std::cout << "  - Ізоляція зворотного променя (Isolation): " << baseRes.isolationDb << " дБ\n\n";

    std::cout << "Аналіз деградації ізоляції при флуктуаціях магнітного поля:\n";
    std::cout << "--------------------------------------------------------\n";
    std::cout << "Відхилення (°) | Ефективний кут | Витік назад (дБ) | Ізоляція (дБ)\n";
    std::cout << "--------------------------------------------------------\n";

    const std::vector<double> errors = {0.0, 0.2, 0.5, 1.0, 2.0, 5.0};
    for (double err : errors) {
        auto res = isolator.runSimulation(err);
        std::cout << std::setw(13) << -err << "° | "
                  << std::setw(13) << (45.0 - err) << "° | "
                  << std::scientific << std::setprecision(3) << std::setw(15) << res.backwardLeakage << " | "
                  << std::fixed << std::setprecision(2) << std::setw(12) << res.isolationDb << " дБ\n";
    }

    return 0;
}
