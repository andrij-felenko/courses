/* Потоковий алгоритм Роймана-Віткама */
size_t simplify_reumann_witkam(const Point* pts, size_t n, double epsilon, Point* out) {
    if (n <= 2) {
        for (size_t i = 0; i < n; ++i) out[i] = pts[i];
        return n;
    }

    double eps_sq = epsilon * epsilon;
    size_t out_count = 0;
    out[out_count++] = pts[0];

    size_t start_idx = 0;
    while (start_idx + 1 < n) {
        Point a = pts[start_idx];
        Point b = pts[start_idx + 1];
        double vx = b.x - a.x;
        double vy = b.y - a.y;
        double seg_sq = vx * vx + vy * vy;

        size_t next_idx = start_idx + 2;
        while (next_idx < n) {
            Point p = pts[next_idx];
            double wx = p.x - a.x;
            double wy = p.y - a.y;
            double cross = wx * vy - wy * vx;
            double dist_sq = (seg_sq > 1e-12) ? ((cross * cross) / seg_sq) : (wx * wx + wy * wy);

            if (dist_sq > eps_sq) {
                break;
            }
            next_idx++;
        }

        if (next_idx < n) {
            out[out_count++] = pts[next_idx - 1];
            start_idx = next_idx - 1;
        } else {
            out[out_count++] = pts[n - 1];
            break;
        }
    }

    return out_count;
}
