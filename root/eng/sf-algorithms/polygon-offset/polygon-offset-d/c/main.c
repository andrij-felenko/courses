#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

typedef enum {
    JOIN_MITER,
    JOIN_BEVEL,
    JOIN_ROUND
} join_type_t;

typedef struct {
    double x;
    double y;
} vec2_t;

// Обчислення зміщеного багатокутника (простий контур)
bool offset_contour(const vec2_t *in_pts, size_t n, double d,
                    join_type_t join, double miter_limit,
                    vec2_t *out_pts, size_t *out_count, size_t max_out) {
    if (n < 3 || !in_pts || !out_pts || !out_count) return false;

    // 1. Обчислення зовнішніх нормалей ребер
    vec2_t *normals = (vec2_t *)malloc(n * sizeof(vec2_t));
    if (!normals) return false;

    for (size_t i = 0; i < n; ++i) {
        size_t next = (i + 1) % n;
        double dx = in_pts[next].x - in_pts[i].x;
        double dy = in_pts[next].y - in_pts[i].y;
        double len = sqrt(dx * dx + dy * dy);
        normals[i] = (len > 1e-9) ? (vec2_t){-dy / len, dx / len} : (vec2_t){0.0, 0.0};
    }

    size_t out_idx = 0;

    // 2. Обробка кожної вершини
    for (size_t i = 0; i < n; ++i) {
        size_t prev = (i + n - 1) % n;
        vec2_t n1 = normals[prev];
        vec2_t n2 = normals[i];
        vec2_t v = in_pts[i];

        double dot = n1.x * n2.x + n1.y * n2.y;
        double cross = n1.x * n2.y - n1.y * n2.x;

        // Майже пряма лінія (180 градусів)
        if (fabs(cross) < 1e-7 && dot > 0.0) {
            if (out_idx < max_out) out_pts[out_idx++] = (vec2_t){v.x + d * n1.x, v.y + d * n1.y};
            continue;
        }

        bool is_convex = (cross > 0.0);

        if (!is_convex) {
            // Увігнутий кут: прямий перетин зміщених прямих
            double denom = fmax(1.0 + dot, 1e-6);
            double k = d / denom;
            if (out_idx < max_out) out_pts[out_idx++] = (vec2_t){v.x + k * (n1.x + n2.x), v.y + k * (n1.y + n2.y)};
        } else {
            // Опуклий кут: застосування обраного типу стику
            if (join == JOIN_MITER) {
                double denom = 1.0 + dot;
                double miter_ratio = (denom > 1e-6) ? sqrt(2.0 / denom) : 1e9;
                if (miter_ratio <= miter_limit) {
                    double k = d / denom;
                    if (out_idx < max_out) out_pts[out_idx++] = (vec2_t){v.x + k * (n1.x + n2.x), v.y + k * (n1.y + n2.y)};
                } else {
                    // Перевищення ліміту -> зріз фаскою
                    if (out_idx < max_out) out_pts[out_idx++] = (vec2_t){v.x + d * n1.x, v.y + d * n1.y};
                    if (out_idx < max_out) out_pts[out_idx++] = (vec2_t){v.x + d * n2.x, v.y + d * n2.y};
                }
            } else if (join == JOIN_BEVEL) {
                if (out_idx < max_out) out_pts[out_idx++] = (vec2_t){v.x + d * n1.x, v.y + d * n1.y};
                if (out_idx < max_out) out_pts[out_idx++] = (vec2_t){v.x + d * n2.x, v.y + d * n2.y};
            }
        }
    }

    free(normals);
    *out_count = out_idx;
    return true;
}
