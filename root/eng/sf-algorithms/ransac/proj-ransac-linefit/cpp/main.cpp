#include <cmath>
#include <optional>
#include <random>
#include <vector>

struct Pt { double x, y; };
struct Line { double a, b, c; };        // a·x + b·y + c = 0, причому a² + b² = 1

// Пряма крізь дві точки. nullopt — вибірка вироджена.
std::optional<Line> line_through(Pt p, Pt q, double min_base) {
    double a = q.y - p.y;               // Δy
    double b = p.x - q.x;               // −Δx
    const double n = std::hypot(a, b);  // = відстань між p і q, тобто база вибірки
    if (n < min_base) return std::nullopt;
    a /= n; b /= n;
    return Line{a, b, -(a * p.x + b * p.y)};
}

int count_inliers(const Line& L, const std::vector<Pt>& pts, double t) {
    int n = 0;
    for (const Pt& p : pts)
        if (std::fabs(L.a * p.x + L.b * p.y + L.c) <= t) ++n;
    return n;
}

std::vector<Pt> collect_inliers(const Line& L, const std::vector<Pt>& pts, double t) {
    std::vector<Pt> in;
    for (const Pt& p : pts)
        if (std::fabs(L.a * p.x + L.b * p.y + L.c) <= t) in.push_back(p);
    return in;
}

// Тотальні найменші квадрати: пряма крізь центроїд уздовж головної осі хмари.
// Мінімізує суму квадратів ПЕРПЕНДИКУЛЯРНИХ відхилень — ту саму міру, якою
// міряла згода. Вертикальних прямих не боїться.
Line refine(const std::vector<Pt>& pts) {
    const double m = static_cast<double>(pts.size());
    double xm = 0.0, ym = 0.0;
    for (const Pt& p : pts) { xm += p.x; ym += p.y; }
    xm /= m; ym /= m;
    double sxx = 0.0, syy = 0.0, sxy = 0.0;
    for (const Pt& p : pts) {
        const double dx = p.x - xm, dy = p.y - ym;
        sxx += dx * dx; syy += dy * dy; sxy += dx * dy;
    }
    const double th = 0.5 * std::atan2(2.0 * sxy, sxx - syy);  // головна вісь
    const double a = -std::sin(th), b = std::cos(th);          // нормаль, одинична
    return Line{a, b, -(a * xm + b * ym)};
}

// Повертає згодні точки; уточнену модель кладе в out.
std::vector<Pt> ransac_line(const std::vector<Pt>& pts, double t, int k,
                            double min_base, std::mt19937& rng, Line& out) {
    const int m = static_cast<int>(pts.size());
    if (m < 2) return {};
    std::uniform_int_distribution<int> pick_i(0, m - 1), pick_j(0, m - 2);
    std::optional<Line> best;
    int best_count = 0;
    for (int it = 0; it < k; ++it) {
        const int i = pick_i(rng);                  // 1. мінімальна вибірка
        int j = pick_j(rng);
        if (j >= i) ++j;                            // рівномірно серед усіх, крім i
        const auto model = line_through(pts[i], pts[j], min_base);   // 2. модель
        if (!model) continue;                       // вироджена — спроба намарне
        const int cnt = count_inliers(*model, pts, t);   // 3. згода: тільки лічимо
        if (cnt > best_count) {                     // 4. новий рекорд
            best = model; best_count = cnt;
        }
    }
    if (!best) return {};
    std::vector<Pt> in = collect_inliers(*best, pts, t);   // список — один раз
    out = refine(in);                                      // уточнення по згодних
    return in;
}
