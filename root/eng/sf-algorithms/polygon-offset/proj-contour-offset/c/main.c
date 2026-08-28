#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef enum {
    JOIN_MITER,
    JOIN_BEVEL,
    JOIN_ROUND
} join_type_t;

typedef struct {
    double x;
    double y;
} point_t;

typedef struct {
    point_t *pts;
    size_t count;
    size_t capacity;
} poly_buffer_t;

static void poly_init(poly_buffer_t *buf, size_t cap) {
    buf->pts = (point_t *)malloc(cap * sizeof(point_t));
    buf->count = 0;
    buf->capacity = cap;
}

static void poly_push(poly_buffer_t *buf, point_t p) {
    if (buf->count >= buf->capacity) {
        buf->capacity = (buf->capacity < 8) ? 8 : buf->capacity * 2;
        buf->pts = (point_t *)realloc(buf->pts, buf->capacity * sizeof(point_t));
    }
    buf->pts[buf->count++] = p;
}

static void poly_free(poly_buffer_t *buf) {
    free(buf->pts);
    buf->pts = NULL;
    buf->count = buf->capacity = 0;
}

// Орієнтована площа багатокутника (формула шнурівки)
static double polygon_area(const point_t *v, size_t n) {
    double area = 0.0;
    for (size_t i = 0, j = n - 1; i < n; j = i++) {
        area += (v[j].x * v[i].y - v[i].x * v[j].y);
    }
    return area * 0.5;
}

// Основна функція зсуву простого многокутника на відстань d
bool polygon_offset(const point_t *in_pts, size_t n, double d,
                    join_type_t join, double miter_limit,
                    int arc_segments, poly_buffer_t *out_poly) {
    if (n < 3 || !in_pts || !out_poly) return false;

    // Враховуємо напрямок обходу (чи CCW)
    double area = polygon_area(in_pts, n);
    bool is_ccw = (area > 0.0);
    double dist = is_ccw ? d : -d;

    // Масив зовнішніх одиничних нормалей для кожного ребра
    point_t *normals = (point_t *)malloc(n * sizeof(point_t));
    if (!normals) return false;

    for (size_t i = 0; i < n; ++i) {
        size_t next = (i + 1) % n;
        double dx = in_pts[next].x - in_pts[i].x;
        double dy = in_pts[next].y - in_pts[i].y;
        double len = sqrt(dx * dx + dy * dy);
        if (len < 1e-9) {
            normals[i] = (point_t){0.0, 0.0};
        } else {
            normals[i] = (point_t){-dy / len, dx / len};
        }
    }

    poly_init(out_poly, n * 2);

    for (size_t i = 0; i < n; ++i) {
        size_t prev = (i + n - 1) % n;
        point_t n1 = normals[prev];
        point_t n2 = normals[i];
        point_t v = in_pts[i];

        double dot = n1.x * n2.x + n1.y * n2.y;
        double cross = n1.x * n2.y - n1.y * n2.x;

        // Майже паралельні ребра (прямий кут 180 градусів)
        if (fabs(cross) < 1e-7 && dot > 0.0) {
            point_t p = { v.x + dist * n1.x, v.y + dist * n1.y };
            poly_push(out_poly, p);
            continue;
        }

        // Векторний добуток > 0 відповідає опуклому куту при обході CCW
        bool is_convex = (cross > 0.0);

        if (!is_convex) {
            // Увігнутий кут: пряме перетинання зміщених ребер
            double denom = 1.0 + dot;
            if (denom < 1e-6) denom = 1e-6;
            double k = dist / denom;
            point_t p = { v.x + k * (n1.x + n2.x), v.y + k * (n1.y + n2.y) };
            poly_push(out_poly, p);
        } else {
            // Опуклий кут: обробка типу стику
            if (join == JOIN_MITER) {
                double denom = 1.0 + dot;
                if (denom > 1e-6) {
                    double miter_ratio = sqrt(2.0 / denom);
                    if (miter_ratio <= miter_limit) {
                        double k = dist / denom;
                        point_t p = { v.x + k * (n1.x + n2.x), v.y + k * (n1.y + n2.y) };
                        poly_push(out_poly, p);
                        continue;
                    }
                }
                // Якщо поріг перевищено — спадаємо до фаски (Bevel)
                point_t p1 = { v.x + dist * n1.x, v.y + dist * n1.y };
                point_t p2 = { v.x + dist * n2.x, v.y + dist * n2.y };
                poly_push(out_poly, p1);
                poly_push(out_poly, p2);
            } else if (join == JOIN_BEVEL) {
                point_t p1 = { v.x + dist * n1.x, v.y + dist * n1.y };
                point_t p2 = { v.x + dist * n2.x, v.y + dist * n2.y };
                poly_push(out_poly, p1);
                poly_push(out_poly, p2);
            } else if (join == JOIN_ROUND) {
                double a1 = atan2(n1.y, n1.x);
                double a2 = atan2(n2.y, n2.x);
                if (a2 < a1) a2 += 2.0 * M_PI;
                int steps = (arc_segments > 1) ? arc_segments : 4;
                for (int s = 0; s <= steps; ++s) {
                    double t = (double)s / steps;
                    double angle = a1 + t * (a2 - a1);
                    point_t p = { v.x + dist * cos(angle), v.y + dist * sin(angle) };
                    poly_push(out_poly, p);
                }
            }
        }
    }

    free(normals);
    return true;
}
