typedef struct {
    size_t start;
    size_t end;
} Range;

/* Ітеративний алгоритм Дугласа-Пекера */
size_t douglas_peucker_iterative(const Point* pts, size_t n, double epsilon, bool* keep) {
    if (n == 0) return 0;
    if (n <= 2) {
        for (size_t i = 0; i < n; ++i) keep[i] = true;
        return n;
    }

    for (size_t i = 0; i < n; ++i) keep[i] = false;
    keep[0] = true;
    keep[n - 1] = true;

    double eps_sq = epsilon * epsilon;

    /* Стек діапазонів: розмір не перевищує n */
    Range* stack = (Range*)malloc(n * sizeof(Range));
    if (!stack) return 0;

    size_t top = 0;
    stack[top++] = (Range){ .start = 0, .end = n - 1 };

    while (top > 0) {
        Range cur = stack[--top];
        if (cur.end <= cur.start + 1) continue;

        double max_dist_sq = 0.0;
        size_t max_idx = cur.start;
        Point a = pts[cur.start];
        Point b = pts[cur.end];

        for (size_t i = cur.start + 1; i < cur.end; ++i) {
            double d_sq = point_to_segment_dist_sq(pts[i], a, b);
            if (d_sq > max_dist_sq) {
                max_dist_sq = d_sq;
                max_idx = i;
            }
        }

        if (max_dist_sq > eps_sq) {
            keep[max_idx] = true;
            stack[top++] = (Range){ .start = cur.start, .end = max_idx };
            stack[top++] = (Range){ .start = max_idx, .end = cur.end };
        }
    }

    free(stack);

    size_t kept_count = 0;
    for (size_t i = 0; i < n; ++i) {
        if (keep[i]) kept_count++;
    }
    return kept_count;
}
