#include <iostream>
#include <vector>
#include <cmath>
#include <functional>
#include <numbers>
#include <iomanip>

struct Vector2D {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr Vector2D operator+(const Vector2D& rhs) const noexcept {
        return {x + rhs.x, y + rhs.y};
    }

    [[nodiscard]] constexpr Vector2D operator*(double scalar) const noexcept {
        return {x * scalar, y * scalar};
    }

    [[nodiscard]] constexpr double dot(const Vector2D& rhs) const noexcept {
        return x * rhs.x + y * rhs.y;
    }
};

using FieldFunction = std::function<Vector2D(double, double)>;

class FieldAnalyzer {
public:
    explicit FieldAnalyzer(FieldFunction field) : field_{std::move(field)} {}

    /* Обчислення циркуляції по замкненому коловому контуру */
    [[nodiscard]] double computeCirculation(Vector2D center, double radius, std::size_t numPoints) const {
        double circulation = 0.0;
        const double dTheta = 2.0 * std::numbers::pi / static_cast<double>(numPoints);

        for (std::size_t i = 0; i < numPoints; ++i) {
            const double theta1 = static_cast<double>(i) * dTheta;
            const double theta2 = static_cast<double>(i + 1) * dTheta;

            const Vector2D p1{center.x + radius * std::cos(theta1), center.y + radius * std::sin(theta1)};
            const Vector2D p2{center.x + radius * std::cos(theta2), center.y + radius * std::sin(theta2)};

            const Vector2D e1 = field_(p1.x, p1.y);
            const Vector2D e2 = field_(p2.x, p2.y);

            const Vector2D dl{p2.x - p1.x, p2.y - p1.y};
            const Vector2D eAvg = (e1 + e2) * 0.5;

            circulation += eAvg.dot(dl);
        }

        return circulation;
    }

    /* Обчислення z-компоненти ротора методом центральних різниць */
    [[nodiscard]] double computeCurlZ(Vector2D point, double h = 1e-5) const {
        const Vector2D eXPlus  = field_(point.x + h, point.y);
        const Vector2D eXMinus = field_(point.x - h, point.y);

        const Vector2D eYPlus  = field_(point.x, point.y + h);
        const Vector2D eYMinus = field_(point.x, point.y - h);

        const double dEy_dx = (eXPlus.y - eXMinus.y) / (2.0 * h);
        const double dEx_dy = (eYPlus.x - eYMinus.x) / (2.0 * h);

        return dEy_dx - dEx_dy;
    }

private:
    FieldFunction field_;
};

int main() {
    std::cout << std::fixed << std::setprecision(12);
    std::cout << "=== ЧИСЕЛЬНИЙ АНАЛІЗ ЦИРКУЛЯЦІЇ ТА РОТОРА (C++) ===\n\n";

    // 1. Потенціальне кулонівське поле
    auto coulombField = [](double x, double y) -> Vector2D {
        double r2 = x * x + y * y;
        if (r2 < 1e-12) r2 = 1e-12;
        double r3 = r2 * std::sqrt(r2);
        return {x / r3, y / r3};
    };

    FieldAnalyzer coulombAnalyzer{coulombField};
    const double rCirc = 2.5;
    const std::size_t nPoints = 1000;

    const double circCoulomb = coulombAnalyzer.computeCirculation({3.0, 3.0}, rCirc, nPoints);
    const double curlCoulomb = coulombAnalyzer.computeCurlZ({3.0, 3.0});

    std::cout << "1. Кулонівське потенціальне поле:\n";
    std::cout << "   Циркуляція по контуру: Gamma = " << circCoulomb << "\n";
    std::cout << "   Ротор у точці (3, 3): rot_z = " << curlCoulomb << "\n\n";

    // 2. Неконсервативне вихорове поле
    constexpr double alpha = 3.0;
    auto vortexField = [alpha](double x, double y) -> Vector2D {
        return {-0.5 * alpha * y, 0.5 * alpha * x};
    };

    FieldAnalyzer vortexAnalyzer{vortexField};
    const double circVortex = vortexAnalyzer.computeCirculation({0.0, 0.0}, rCirc, nPoints);
    const double curlVortex = vortexAnalyzer.computeCurlZ({1.0, 1.0});
    const double exactCirc  = alpha * std::numbers::pi * rCirc * rCirc;

    std::cout << "2. Індуковане вихорове поле (alpha=" << alpha << "):\n";
    std::cout << "   Чисельна циркуляція:   Gamma = " << circVortex << "\n";
    std::cout << "   Аналітична циркуляція: Gamma = " << exactCirc << "\n";
    std::cout << "   Ротор у точці (1, 1): rot_z = " << curlVortex << "\n";

    return 0;
}
