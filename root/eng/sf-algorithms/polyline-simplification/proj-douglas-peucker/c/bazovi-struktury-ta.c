#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    double x;
    double y;
} Point;

/* Обчислення квадрата відстані від точки P до відрізка AB */
static inline double point_to_segment_dist_sq(Point p, Point a, Point b) {
    double vx = b.x - a.x;
    double vy = b.y - a.y;
    double wx = p.x - a.x;
    double wy = p.y - a.y;

    double seg_len_sq = vx * vx + vy * vy;
    if (seg_len_sq < 1e-12) {
        /* Відрізок вироджений у точку */
        return wx * wx + wy * wy;
    }

    double t = (wx * vx + wy * vy) / seg_len_sq;
    if (t <= 0.0) {
        /* Найближча точка — початок відрізка A */
        return wx * wx + wy * wy;
    }
    if (t >= 1.0) {
        /* Найближча точка — кінець відрізка B */
        double bx = p.x - b.x;
        double by = p.y - b.y;
        return bx * bx + by * by;
    }

    /* Основа перпендикуляра падає всередину відрізка */
    double cross = wx * vy - wy * vx;
    return (cross * cross) / seg_len_sq;
}
