#include <algorithm>
#include <cmath>
#include <functional>
#include <vector>

namespace distort {

inline constexpr double R  = 6371008.8;                 // середній радіус WGS-84, м
inline constexpr double PI = 3.14159265358979323846;

struct XY { double x, y; };
using Forward = std::function<XY(double phi, double lam)>;   // радіани → одиниці карти

struct Tissot { double a, b, area, omega; };            // omega у градусах

// Спотворення в точці: h — крок центральної різниці, радіани.
Tissot tissot(const Forward& f, double phi, double lam, double h = 1e-6) {
    const XY e1 = f(phi, lam + h), e2 = f(phi, lam - h);   // СХІД — перший стовпець
    const XY n1 = f(phi + h, lam), n2 = f(phi - h, lam);   // ПІВНІЧ — другий
    const double de = 2.0 * h * R * std::cos(phi);         // метрів по землі
    const double dn = 2.0 * h * R;

    const double m11 = (e1.x - e2.x) / de, m12 = (n1.x - n2.x) / dn;
    const double m21 = (e1.y - e2.y) / de, m22 = (n1.y - n2.y) / dn;

    const double E = 0.5 * (m11 + m22), F = 0.5 * (m11 - m22);
    const double G = 0.5 * (m21 + m12), H = 0.5 * (m21 - m12);
    const double Q = std::hypot(E, H), S = std::hypot(F, G);   // конформна / антиконформна

    const double a = Q + S, b = std::fabs(Q - S);
    const double lo = std::min(Q, S), hi = std::max(Q, S);
    const double om = hi > 0.0 ? 2.0 * std::asin(std::min(1.0, lo / hi)) * 180.0 / PI : 0.0;
    return { a, b, a * b, om };
}

struct Score { double area_lo, area_hi, omega_max, omega_med; };

// Найгірше й медіанне спотворення по сітці над прямокутником (градуси).
Score sweep(const Forward& f, double south, double west, double north, double east, int n = 61) {
    std::vector<double> area, omega;
    area.reserve(std::size_t(n) * n);
    omega.reserve(std::size_t(n) * n);
    for (int i = 0; i < n; ++i) {
        const double phi = (south + (north - south) * i / (n - 1)) * PI / 180.0;
        for (int j = 0; j < n; ++j) {
            const double lam = (west + (east - west) * j / (n - 1)) * PI / 180.0;
            const Tissot t = tissot(f, phi, lam);
            area.push_back(t.area);
            omega.push_back(t.omega);
        }
    }
    std::sort(area.begin(), area.end());
    std::sort(omega.begin(), omega.end());
    const double med = area[area.size() / 2];      // калібрування номінального масштабу
    return { area.front() / med, area.back() / med,
             omega.back(), omega[omega.size() / 2] };
}

}  // namespace distort

namespace proj {

using distort::PI;  using distort::R;  using distort::XY;

auto mercator(double lam0) {
    return [lam0](double phi, double lam) -> XY {
        return { R * (lam - lam0), R * std::asinh(std::tan(phi)) };
    };
}

// Циліндрична рівновелика Ламберта, нормальна паралель phi1.
auto lambert_cea(double phi1, double lam0) {
    const double c = std::cos(phi1);
    return [c, lam0](double phi, double lam) -> XY {
        return { R * (lam - lam0) * c, R * std::sin(phi) / c };
    };
}

// Конічна конформна Ламберта на двох стандартних паралелях.
auto lambert_cc(double phi1, double phi2, double phi0, double lam0) {
    auto t = [](double p) { return std::tan(PI / 4 + p / 2); };
    const double n    = std::log(std::cos(phi1) / std::cos(phi2)) / std::log(t(phi2) / t(phi1));
    const double F    = std::cos(phi1) * std::pow(t(phi1), n) / n;
    const double rho0 = R * F / std::pow(t(phi0), n);
    return [t, n, F, rho0, lam0](double phi, double lam) -> XY {
        const double rho = R * F / std::pow(t(phi), n);
        const double th  = n * (lam - lam0);
        return { rho * std::sin(th), rho0 - rho * std::cos(th) };
    };
}

// Азимутальна рівнопроміжна з центром (phi0, lam0).
auto azimuthal_ed(double phi0, double lam0) {
    return [phi0, lam0](double phi, double lam) -> XY {
        const double cc = std::sin(phi0) * std::sin(phi)
                        + std::cos(phi0) * std::cos(phi) * std::cos(lam - lam0);
        const double c  = std::acos(std::clamp(cc, -1.0, 1.0));   // кутова відстань від центра
        const double k  = c < 1e-10 ? 1.0 : c / std::sin(c);
        return { R * k * std::cos(phi) * std::sin(lam - lam0),
                 R * k * (std::cos(phi0) * std::sin(phi)
                        - std::sin(phi0) * std::cos(phi) * std::cos(lam - lam0)) };
    };
}

}  // namespace proj
