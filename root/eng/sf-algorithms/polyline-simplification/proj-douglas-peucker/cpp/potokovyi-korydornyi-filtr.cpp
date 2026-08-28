/* Потоковий фільтр Роймана-Віткама */
[[nodiscard]] std::vector<Point> simplifyReumannWitkam(std::span<const Point> points, double epsilon) {
    const size_t n = points.size();
    if (n <= 2) {
        return std::vector<Point>(points.begin(), points.end());
    }

    const double epsSq = epsilon * epsilon;
    std::vector<Point> result;
    result.reserve(n / 2);
    result.push_back(points[0]);

    size_t startIdx = 0;
    while (startIdx + 1 < n) {
        const Point& a = points[startIdx];
        const Point& b = points[startIdx + 1];
        const double vx = b.x - a.x;
        const double vy = b.y - a.y;
        const double segSq = vx * vx + vy * vy;

        size_t nextIdx = startIdx + 2;
        while (nextIdx < n) {
            const Point& p = points[nextIdx];
            const double wx = p.x - a.x;
            const double wy = p.y - a.y;
            const double cross = wx * vy - wy * vx;
            const double distSq = (segSq > 1e-12) ? ((cross * cross) / segSq) : (wx * wx + wy * wy);

            if (distSq > epsSq) {
                break;
            }
            ++nextIdx;
        }

        if (nextIdx < n) {
            result.push_back(points[nextIdx - 1]);
            startIdx = nextIdx - 1;
        } else {
            result.push_back(points[n - 1]);
            break;
        }
    }

    return result;
}
