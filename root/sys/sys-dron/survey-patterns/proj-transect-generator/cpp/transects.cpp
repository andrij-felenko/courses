// збірка: g++ -std=c++17 -O2 transects.cpp -o transects
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <utility>
#include <vector>

struct Vec2     { double x{}; double y{}; };            // x — на північ, y — на схід, метри
struct Transect { Vec2 a{}; Vec2 b{}; };                // галс: початок і кінець
struct Box      { double xLo{}, xHi{}, yLo{}, yHi{}; };

using Polygon = std::vector<Vec2>;

constexpr int    kMaxTransects = 1000;                  // стеля кількості галсів
constexpr double kMinLength    = 1e-6;                  // коротше — це дотик, а не галс
constexpr double kDegToRad     = 0.017453292519943295;  // π / 180

Vec2 rotate(const Vec2 &p, const Vec2 &c, double rad) {
    const double dx = p.x - c.x, dy = p.y - c.y;
    const double s = std::sin(rad), k = std::cos(rad);
    return { c.x + dx * k - dy * s, c.y + dx * s + dy * k };
}

Box bounds(const Polygon &poly) {
    Box b{ poly[0].x, poly[0].x, poly[0].y, poly[0].y };
    for (const Vec2 &p : poly) {
        b.xLo = std::min(b.xLo, p.x);  b.xHi = std::max(b.xHi, p.x);
        b.yLo = std::min(b.yLo, p.y);  b.yHi = std::max(b.yHi, p.y);
    }
    return b;
}

double clampAngle90(double deg) {
    while (deg >  90.0) deg -= 180.0;
    while (deg < -90.0) deg += 180.0;
    return deg;
}
