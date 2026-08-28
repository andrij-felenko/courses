#include <stdio.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    double x;
    double y;
} Point2D;

typedef struct {
    Point2D start;
    Point2D end;
    int site_a;
    int site_b;
    bool is_ray;
} Edge2D;

/* Обчислення евклідової відстані між двома точками */
static inline double point_dist_sq(Point2D a, Point2D b) {
    double dx = a.x - b.x;
    double dy = a.y - b.y;
    return dx * dx + dy * dy;
}

/* Лінійний пошук найближчого сайта за O(N) для контрольної перевірки */
int find_nearest_site_linear(const Point2D* sites, int n, Point2D query) {
    if (n <= 0) return -1;
    int best_idx = 0;
    double min_d2 = point_dist_sq(sites[0], query);

    for (int i = 1; i < n; ++i) {
        double d2 = point_dist_sq(sites[i], query);
        if (d2 < min_d2) {
            min_d2 = d2;
            best_idx = i;
        }
    }
    return best_idx;
}
