#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <numeric>

// Двовимірний вектор та операції над ним
struct Vector2D {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr Vector2D operator+(const Vector2D& other) const noexcept {
        return {x + other.x, y + other.y};
    }

    [[nodiscard]] constexpr Vector2D operator-(const Vector2D& other) const noexcept {
        return {x - other.x, y - other.y};
    }

    [[nodiscard]] constexpr Vector2D operator*(double scalar) const noexcept {
        return {x * scalar, y * scalar};
    }

    [[nodiscard]] constexpr double dot(const Vector2D& other) const noexcept {
        return x * other.x + y * other.y;
    }

    [[nodiscard]] double lengthSquared() const noexcept {
        return x * x + y * y;
    }
};

// Провідник зі струмом
struct Wire {
    Vector2D position;
    double current{0.0}; // Струм у Амперах
};

class AmpereSimulator {
public:
    static constexpr double mu_0 = 4.0 * std::numbers::pi * 1e-7;

    /**
     * Обчислює вектор магнітної індукції B у точці point від усіх провідників.
     */
    [[nodiscard]] static Vector2D computeField(Vector2D point, const std::vector<Wire>& wires) noexcept {
        Vector2D b_total{0.0, 0.0};
        constexpr double eps_sq = 1e-14;

        for (const auto& wire : wires) {
            Vector2D r = point - wire.position;
            double r2 = r.lengthSquared();

            if (r2 < eps_sq) {
                continue; // Ігноруємо точку джерела
            }

            double coeff = (mu_0 * wire.current) / (2.0 * std::numbers::pi * r2);
            b_total.x += -coeff * r.y;
            b_total.y +=  coeff * r.x;
        }

        return b_total;
    }

    /**
     * Обчислює циркуляцію поля B вздовж замкненого контуру.
     */
    [[nodiscard]] static double calculateCirculation(const std::vector<Vector2D>& contour, 
                                                      const std::vector<Wire>& wires) noexcept {
        if (contour.size() < 3) return 0.0;

        double circulation = 0.0;
        const size_t n = contour.size();

        for (size_t i = 0; i < n; ++i) {
            const Vector2D& p1 = contour[i];
            const Vector2D& p2 = contour[(i + 1) % n];

            Vector2D mid = (p1 + p2) * 0.5;
            Vector2D dl = p2 - p1;

            Vector2D b = computeField(mid, wires);
            circulation += b.dot(dl);
        }

        return circulation;
    }
};

int main() {
    std::cout << "=====================================================\n";
    std::cout << "   C++ Обчислювальний модуль закону Ампера           \n";
    std::cout << "=====================================================\n\n";

    // 1. Ініціалізація джерел струму
    const std::vector<Wire> wires = {
        { .position = { 0.02,  0.01}, .current =  12.5 }, // Всередині
        { .position = {-0.04, -0.03}, .current =  -5.0 }, // Всередині
        { .position = { 0.35,  0.40}, .current =  50.0 }  // Зовні
    };

    // 2. Генерація замкненого контуру у формі прямокутника зі зрізаними кутами
    constexpr size_t segments_per_side = 500;
    std::vector<Vector2D> contour;
    contour.reserve(segments_per_side * 4);

    constexpr double x_min = -0.15, x_max = 0.15;
    constexpr double y_min = -0.10, y_max = 0.10;

    // Нижня сторона (зліва направо)
    for (size_t i = 0; i < segments_per_side; ++i) {
        double t = static_cast<double>(i) / segments_per_side;
        contour.push_back({ x_min + t * (x_max - x_min), y_min });
    }
    // Права сторона (знизу вгору)
    for (size_t i = 0; i < segments_per_side; ++i) {
        double t = static_cast<double>(i) / segments_per_side;
        contour.push_back({ x_max, y_min + t * (y_max - y_min) });
    }
    // Верхня сторона (справа наліво)
    for (size_t i = 0; i < segments_per_side; ++i) {
        double t = static_cast<double>(i) / segments_per_side;
        contour.push_back({ x_max - t * (x_max - x_min), y_max });
    }
    // Ліва сторона (згори вниз)
    for (size_t i = 0; i < segments_per_side; ++i) {
        double t = static_cast<double>(i) / segments_per_side;
        contour.push_back({ x_min, y_max - t * (y_max - y_min) });
    }

    // 3. Розрахунок чисельної циркуляції
    const double calc_circ = AmpereSimulator::calculateCirculation(contour, wires);

    // 4. Порівняння з теорією
    const double enclosed_current = wires[0].current + wires[1].current;
    const double theory_circ = AmpereSimulator::mu_0 * enclosed_current;
    const double rel_error = std::abs(calc_circ - theory_circ) / theory_circ * 100.0;

    std::cout << std::fixed << std::setprecision(6);
    std::cout << "Параметри моделювання:\n";
    std::cout << "  Кількість точок контуру: " << contour.size() << "\n";
    std::cout << "  Сумарний охоплений струм: " << enclosed_current << " A\n\n";

    std::cout << std::scientific << std::setprecision(9);
    std::cout << "  Чисельна циркуляція ∮ B·dl:  " << calc_circ << " Тл·м\n";
    std::cout << "  Теоретична циркуляція μ₀·I:  " << theory_circ << " Тл·м\n";
    std::cout << std::fixed << std::setprecision(6);
    std::cout << "  Відносна похибка розрахунку: " << rel_error << " %\n";

    return 0;
}
