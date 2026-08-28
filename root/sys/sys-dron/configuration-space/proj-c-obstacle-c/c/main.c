#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define MAX_C_VERTICES 64

typedef struct {
    double x;
    double y;
} vec2_t;

typedef struct {
    vec2_t vertices[MAX_C_VERTICES];
    size_t count;
} polygon_t;

static inline double cross_2d(vec2_t a, vec2_t b) {
    return a.x * b.y - a.y * b.x;
}

static inline vec2_t vec_sub(vec2_t a, vec2_t b) {
    return (vec2_t){a.x - b.x, a.y - b.y};
}

static inline vec2_t vec_add(vec2_t a, vec2_t b) {
    return (vec2_t){a.x + b.x, a.y + b.y};
}

static inline vec2_t vec_neg(vec2_t a) {
    return (vec2_t){-a.x, -a.y};
}

static size_t find_bottom_left_index(const polygon_t *poly) {
    size_t min_idx = 0;
    for (size_t i = 1; i < poly->count; ++i) {
        if (poly->vertices[i].y < poly->vertices[min_idx].y ||
            (fabs(poly->vertices[i].y - poly->vertices[min_idx].y) < 1e-9 &&
             poly->vertices[i].x < poly->vertices[min_idx].x)) {
            min_idx = i;
        }
    }
    return min_idx;
}

/* Інверсія форми робота -A з відновленням напрямку CCW */
static polygon_t invert_and_reorder_polygon(const polygon_t *poly) {
    polygon_t result;
    result.count = poly->count;
    for (size_t i = 0; i < poly->count; ++i) {
        result.vertices[i] = vec_neg(poly->vertices[poly->count - 1 - i]);
    }
    return result;
}

/* Лінійна сума Мінковського опуклих контурів O(N + M) */
polygon_t minkowski_sum_convex(const polygon_t *poly_b, const polygon_t *poly_a_neg) {
    polygon_t result = { .count = 0 };
    if (poly_b->count == 0 || poly_a_neg->count == 0) return result;

    size_t i = find_bottom_left_index(poly_b);
    size_t j = find_bottom_left_index(poly_a_neg);

    size_t count_b = poly_b->count;
    size_t count_a = poly_a_neg->count;

    size_t steps_b = 0;
    size_t steps_a = 0;

    while (steps_b < count_b || steps_a < count_a) {
        if (result.count >= MAX_C_VERTICES) break;
        result.vertices[result.count++] = vec_add(poly_b->vertices[i], poly_a_neg->vertices[j]);

        vec2_t edge_b = vec_sub(poly_b->vertices[(i + 1) % count_b], poly_b->vertices[i]);
        vec2_t edge_a = vec_sub(poly_a_neg->vertices[(j + 1) % count_a], poly_a_neg->vertices[j]);

        double cp = cross_2d(edge_b, edge_a);

        if (steps_b < count_b && steps_a < count_a) {
            if (cp > 1e-9) {
                i = (i + 1) % count_b;
                steps_b++;
            } else if (cp < -1e-9) {
                j = (j + 1) % count_a;
                steps_a++;
            } else {
                /* Колінеарні ребра: робимо спільний крок */
                i = (i + 1) % count_b;
                j = (j + 1) % count_a;
                steps_b++;
                steps_a++;
            }
        } else if (steps_b < count_b) {
            i = (i + 1) % count_b;
            steps_b++;
        } else {
            j = (j + 1) % count_a;
            steps_a++;
        }
    }
    return result;
}

polygon_t compute_c_obstacle(const polygon_t *obstacle, const polygon_t *robot) {
    polygon_t robot_neg = invert_and_reorder_polygon(robot);
    return minkowski_sum_convex(obstacle, &robot_neg);
}

int main(void) {
    polygon_t robot = {
        .vertices = {
            {-0.4, -0.3},
            { 0.4, -0.3},
            { 0.4,  0.3},
            {-0.4,  0.3}
        },
        .count = 4
    };

    polygon_t obstacle = {
        .vertices = {
            {2.0, 1.0},
            {4.0, 1.0},
            {3.0, 3.0}
        },
        .count = 3
    };

    polygon_t c_obs = compute_c_obstacle(&obstacle, &robot);

    printf("Побудовано C-перешкоду (%zu вершин):\n", c_obs.count);
    for (size_t i = 0; i < c_obs.count; ++i) {
        printf("  V[%zu] = (%.2f, %.2f)\n", i, c_obs.vertices[i].x, c_obs.vertices[i].y);
    }

    return 0;
}
