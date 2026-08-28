#include <stdbool.h>
#include <stdlib.h>

typedef struct {
    double x;
    double y;
} Point;

typedef struct {
    size_t start;
    size_t end;
} SegmentRange;

static inline double calc_dist_sq(Point p, Point a, Point b) {
    double vx = b.x - a.x, vy = b.y - a.y;
    double wx = p.x - a.x, wy = p.y - a.y;
    double seg_sq = vx * vx + vy * vy;
    if (seg_sq < 1e-12) return wx * wx + wy * wy;

    double t = (wx * vx + wy * vy) / seg_sq;
    if (t <= 0.0) return wx * wx + wy * wy;
    if (t >= 1.0) {
        double bx = p.x - b.x, by = p.y - b.y;
        return bx * bx + by * by;
    }
    double cross = wx * vy - wy * vx;
    return (cross * cross) / seg_sq;
}

/* Ітеративний Дуглас-Пекер: повертає кількість збережених точок у масиві keep */
size_t rdp_simplify_c(const Point* pts, size_t n, double eps, bool* keep) {
    if (n == 0) return 0;
    for (size_t i = 0; i < n; ++i) keep[i] = false;
    keep[0] = true;
    keep[n - 1] = true;
    if (n <= 2) return n;

    SegmentRange* stack = (SegmentRange*)malloc(n * sizeof(SegmentRange));
    if (!stack) return 0;

    size_t top = 0;
    stack[top++] = (SegmentRange){ .start = 0, .end = n - 1 };
    double eps_sq = eps * eps;

    while (top > 0) {
        SegmentRange range = stack[--top];
        if (range.end <= range.start + 1) continue;

        double max_d_sq = 0.0;
        size_t max_idx = range.start;
        Point a = pts[range.start], b = pts[range.end];

        for (size_t i = range.start + 1; i < range.end; ++i) {
            double d_sq = calc_dist_sq(pts[i], a, b);
            if (d_sq > max_d_sq) {
                max_d_sq = d_sq;
                max_idx = i;
            }
        }

        if (max_d_sq > eps_sq) {
            keep[max_idx] = true;
            stack[top++] = (SegmentRange){ .start = range.start, .end = max_idx };
            stack[top++] = (SegmentRange){ .start = max_idx, .end = range.end };
        }
    }

    free(stack);
    size_t count = 0;
    for (size_t i = 0; i < n; ++i) {
        if (keep[i]) count++;
    }
    return count;
}
