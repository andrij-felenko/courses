#include <vector>
#include <array>
#include <cmath>
#include <cstdlib>

struct Pt { double x, y; };

// пряма ax + by + c = 0 через дві точки, нормована (a² + b² = 1)
std::array<double, 3> line_through(Pt p, Pt q) {
    double a = q.y - p.y, b = p.x - q.x, c = -(a * p.x + b * p.y);
    double n = std::hypot(a, b);
    return {a / n, b / n, c / n};
}

// найкращу модель кладе у best; повертає індекси згодних точок
std::vector<int> ransac_line(const std::vector<Pt>& pts, double t, int k,
                             std::array<double, 3>& best) {
    std::vector<int> best_in;
    int m = pts.size();
    for (int it = 0; it < k; ++it) {
        int i = rand() % m, j = rand() % m;        // 1. мінімальна вибірка — 2 точки
        if (i == j) continue;
        auto [a, b, c] = line_through(pts[i], pts[j]);   // 2. модель по вибірці
        std::vector<int> in;
        for (int r = 0; r < m; ++r)                // 3. згода: хто ближче за t
            if (std::fabs(a * pts[r].x + b * pts[r].y + c) <= t) in.push_back(r);
        if (in.size() > best_in.size()) {          // 4. новий рекорд згоди
            best = {a, b, c}; best_in = in;
        }
    }
    return best_in;                                // уточнити по best_in — окремо
}
