#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <limits>
#include <unordered_map>
#include <vector>

constexpr double PI = 3.14159265358979323846;

struct Vec3 { double x, y, z; };

inline Vec3   operator-(Vec3 a, Vec3 b) { return {a.x - b.x, a.y - b.y, a.z - b.z}; }
inline double dot(Vec3 a, Vec3 b)       { return a.x * b.x + a.y * b.y + a.z * b.z; }
inline Vec3   cross(Vec3 a, Vec3 b)     { return {a.y * b.z - a.z * b.y,
                                                  a.z * b.x - a.x * b.z,
                                                  a.x * b.y - a.y * b.x}; }
inline double len(Vec3 a)               { return std::sqrt(dot(a, a)); }

struct Mesh {
    std::vector<Vec3> pos;                        // координати вершин
    std::vector<std::array<uint32_t, 3>> tri;     // трикутники: індекси в pos
};

// Кут при вершині a в трикутнику (a, b, c).
// atan2, а не acos: немає ділення на довжини, немає що затискати, і точність
// не сідає ні біля 0, ні біля π.
inline double corner(Vec3 a, Vec3 b, Vec3 c) {
    const Vec3 u = b - a, v = c - a;
    return std::atan2(len(cross(u, v)), dot(u, v));
}

struct Result {
    std::vector<double>  K;            // NaN там, де величина не визначена
    std::vector<uint8_t> boundary;     // край сітки або злам многовиду
    double   total_defect = 0.0;       // Σ(2π − Σθ); для замкненої сітки = 2π·χ
    uint32_t edges = 0;
    uint32_t skipped = 0;              // вироджені трикутники
};

Result gaussian_curvature(const Mesh& m, bool mixed = true) {
    const size_t n = m.pos.size();
    Result out;
    std::vector<double> angle(n, 0.0), area(n, 0.0);
    std::unordered_map<uint64_t, uint32_t> use;    // ребро → скільки трикутників його ділять
    use.reserve(m.tri.size() * 3);

    for (const auto& f : m.tri) {
        for (int k = 0; k < 3; ++k) {              // топологія — до всякої геометрії
            const uint32_t a = std::min(f[k], f[(k + 1) % 3]);
            const uint32_t b = std::max(f[k], f[(k + 1) % 3]);
            ++use[(uint64_t(a) << 32) | b];
        }

        const Vec3 p[3] = { m.pos[f[0]], m.pos[f[1]], m.pos[f[2]] };
        double e2[3];                              // e2[k] = |p[k+1] − p[k]|²
        for (int k = 0; k < 3; ++k) {
            const Vec3 d = p[(k + 1) % 3] - p[k];
            e2[k] = dot(d, d);
        }
        const double twoA = len(cross(p[1] - p[0], p[2] - p[0]));
        // Вироджений: площа мізерна проти квадрата найдовшої сторони. Абсолютний
        // поріг не годиться — сітка буває в метрах, а буває в мікронах.
        if (twoA <= 1e-12 * std::max({e2[0], e2[1], e2[2]})) { ++out.skipped; continue; }
        const double A = 0.5 * twoA;

        double th[3];
        for (int k = 0; k < 3; ++k) th[k] = corner(p[k], p[(k + 1) % 3], p[(k + 2) % 3]);
        for (int k = 0; k < 3; ++k) angle[f[k]] += th[k];

        const bool acute = th[0] <= PI / 2 && th[1] <= PI / 2 && th[2] <= PI / 2;
        if (!mixed) {                              // барицентрична A/3
            for (int k = 0; k < 3; ++k) area[f[k]] += A / 3.0;
        } else if (acute) {                        // клітина Вороного лежить у трикутнику
            for (int k = 0; k < 3; ++k)
                area[f[k]] += (e2[k]           / std::tan(th[(k + 2) % 3]) +
                               e2[(k + 2) % 3] / std::tan(th[(k + 1) % 3])) / 8.0;
        } else {                                   // тупий кут: Вороного вилазить назовні
            for (int k = 0; k < 3; ++k) area[f[k]] += (th[k] > PI / 2) ? A / 2.0 : A / 4.0;
        }
    }

    out.edges = uint32_t(use.size());
    out.boundary.assign(n, 0);
    for (const auto& [key, cnt] : use)
        if (cnt != 2) {                            // 1 — край, ≥3 — сітка не многовид
            out.boundary[uint32_t(key >> 32)] = 1;
            out.boundary[uint32_t(key)]       = 1;
        }

    out.K.assign(n, std::numeric_limits<double>::quiet_NaN());
    for (size_t i = 0; i < n; ++i) {
        if (angle[i] == 0.0) continue;             // вершина без жодного трикутника
        out.total_defect += 2.0 * PI - angle[i];
        if (out.boundary[i]) continue;             // на краю 2π не має підстав
        out.K[i] = (2.0 * PI - angle[i]) / area[i];
    }
    return out;
}
