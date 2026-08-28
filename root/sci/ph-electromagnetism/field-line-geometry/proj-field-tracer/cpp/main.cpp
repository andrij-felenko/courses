#include <iostream>
#include <vector>
#include <cmath>
#include <memory>
#include <algorithm>

// Структура представлення точкового заряду
struct Charge {
    double q; // Заряд в Кулонах
    double x; // Позиція X
    double y; // Позиція Y
};

// Двовимірна точка / вектор
struct Point2D {
    double x{0.0};
    double y{0.0};

    Point2D operator+(const Point2D& other) const { return {x + other.x, y + other.y}; }
    Point2D operator*(double scalar) const { return {x * scalar, y * scalar}; }
};

class FieldTracer2D {
private:
    std::vector<Charge> charges_;
    static constexpr double k_e = 8.9875e9;

public:
    explicit FieldTracer2D(std::vector<Charge> charges) 
        : charges_(std::move(charges)) {}

    // Обчислення вектора напруженості електричного поля E(x, y)
    Point2D calcField(double x, double y) const {
        double ex = 0.0;
        double ey = 0.0;
        for (const auto& c : charges_) {
            double dx = x - c.x;
            double dy = y - c.y;
            double r2 = dx * dx + dy * dy;
            double r = std::sqrt(r2);
            if (r < 1e-6) continue;
            double e_mag = k_e * c.q / r2;
            ex += e_mag * (dx / r);
            ey += e_mag * (dy / r);
        }
        return {ex, ey};
    }

    // Отримання нормованого вектора напрямку лінії E / |E|
    Point2D getUnitField(double x, double y, double direction = 1.0) const {
        Point2D e = calcField(x, y);
        double emag = std::hypot(e.x, e.y);
        if (emag < 1e-12) return {0.0, 0.0};
        return {direction * (e.x / emag), direction * (e.y / emag)};
    }

    // Один крок чисельного інтегрування RK4
    Point2D rk4Step(double x, double y, double ds, double direction = 1.0) const {
        Point2D k1 = getUnitField(x, y, direction);
        if (k1.x == 0.0 && k1.y == 0.0) return {x, y};

        Point2D k2 = getUnitField(x + 0.5 * ds * k1.x, y + 0.5 * ds * k1.y, direction);
        Point2D k3 = getUnitField(x + 0.5 * ds * k2.x, y + 0.5 * ds * k2.y, direction);
        Point2D k4 = getUnitField(x + ds * k3.x, y + ds * k3.y, direction);

        double nx = x + (ds / 6.0) * (k1.x + 2.0 * k2.x + 2.0 * k3.x + k4.x);
        double ny = y + (ds / 6.0) * (k1.y + 2.0 * k2.y + 2.0 * k3.y + k4.y);
        return {nx, ny};
    }

    // Трасування однієї силової лінії
    std::vector<Point2D> traceLine(double startX, double startY, double ds = 0.01, 
                                   int maxSteps = 1500, double direction = 1.0) const {
        std::vector<Point2D> line;
        line.reserve(maxSteps);
        line.push_back({startX, startY});

        double cx = startX;
        double cy = startY;
        const double rCutoff = 0.035;

        for (int step = 0; step < maxSteps; ++step) {
            Point2D np = rk4Step(cx, cy, ds, direction);

            // Перевірка просторових меж [-1.5, 1.5]
            if (std::abs(np.x) > 1.5 || std::abs(np.y) > 1.5) break;

            // Перевірка наближення до зарядів-стоків
            bool hitSink = false;
            for (const auto& c : charges_) {
                if (std::hypot(np.x - c.x, np.y - c.y) < rCutoff) {
                    hitSink = true;
                    break;
                }
            }

            line.push_back(np);
            if (hitSink) break;

            cx = np.x;
            cy = np.y;
        }
        return line;
    }

    // Генерація повного набору силових ліній
    std::vector<std::vector<Point2D>> generateFieldMap(int linesPerCharge = 12, double ds = 0.008) const {
        std::vector<std::vector<Point2D>> allLines;
        const double rStart = 0.045;
        const double pi = std::acos(-1.0);

        for (const auto& c : charges_) {
            double direction = (c.q > 0.0) ? 1.0 : -1.0;
            int numLines = static_cast<int>(linesPerCharge * std::abs(c.q) / 1e-9);

            for (int i = 0; i < numLines; ++i) {
                double angle = 2.0 * pi * i / numLines;
                double sx = c.x + rStart * std::cos(angle);
                double sy = c.y + rStart * std::sin(angle);
                allLines.push_back(traceLine(sx, sy, ds, 1500, direction));
            }
        }
        return allLines;
    }
};

int main() {
    // Конфігурація системи трьох зарядів
    std::vector<Charge> charges = {
        { 1e-9, -0.4, 0.0},
        { 1e-9,  0.4, 0.0},
        {-2e-9,  0.0, 0.5}
    };

    FieldTracer2D tracer(charges);
    auto fieldLines = tracer.generateFieldMap(12, 0.008);

    std::cout << "Успішно розраховано " << fieldLines.size() << " силових ліній." << std::endl;
    return 0;
}
