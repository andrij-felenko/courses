#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <float.h>
#include <stdbool.h>

typedef struct {
    float *coords;
    int id;
} point_t;

typedef struct vp_node {
    point_t vantage_point;
    float threshold;
    struct vp_node *inside;
    struct vp_node *outside;
} vp_node_t;

typedef struct {
    vp_node_t *root;
    int dim;
    size_t distance_evals;
} vp_tree_t;

/* Обчислення квадрата евклідової відстані */
float squared_euclidean(const float *a, const float *b, int dim) {
    float sum = 0.0f;
    for (int i = 0; i < dim; ++i) {
        float diff = a[i] - b[i];
        sum += diff * diff;
    }
    return sum;
}

/* 1. Лінійний точний перебір */
point_t linear_scan_nn(const point_t *points, size_t n, int dim,
                       const float *query, size_t *evals) {
    point_t best = points[0];
    float min_dist_sq = FLT_MAX;
    *evals = 0;

    for (size_t i = 0; i < n; ++i) {
        float d_sq = squared_euclidean(points[i].coords, query, dim);
        (*evals)++;
        if (d_sq < min_dist_sq) {
            min_dist_sq = d_sq;
            best = points[i];
        }
    }
    return best;
}

/* Порівняння відстаней для qsort */
static const float *g_vp_coord;
static int g_dim;
static int compare_points(const void *a, const void *b) {
    const point_t *p1 = (const point_t *)a;
    const point_t *p2 = (const point_t *)b;
    float d1 = squared_euclidean(p1->coords, g_vp_coord, g_dim);
    float d2 = squared_euclidean(p2->coords, g_vp_coord, g_dim);
    return (d1 > d2) - (d1 < d2);
}

/* Рекурсивна побудова VP-дерева */
vp_node_t* vp_build_recursive(point_t *points, size_t n, int dim) {
    if (n == 0) return NULL;

    vp_node_t *node = (vp_node_t *)malloc(sizeof(vp_node_t));
    node->vantage_point = points[0];

    if (n == 1) {
        node->threshold = 0.0f;
        node->inside = NULL;
        node->outside = NULL;
        return node;
    }

    /* Сортуємо решту точок відносно vantage_point для знаходження медіани */
    g_vp_coord = node->vantage_point.coords;
    g_dim = dim;
    qsort(points + 1, n - 1, sizeof(point_t), compare_points);

    size_t mid = 1 + (n - 1) / 2;
    node->threshold = sqrtf(squared_euclidean(points[mid].coords, g_vp_coord, dim));

    node->inside = vp_build_recursive(points + 1, mid - 1, dim);
    node->outside = vp_build_recursive(points + mid, n - mid, dim);

    return node;
}

/* Рекурсивний пошук у VP-дереві з відтинанням */
void vp_search_recursive(const vp_node_t *node, const float *query, int dim,
                         float *best_dist, point_t *best_point, size_t *evals) {
    if (!node) return;

    float d = sqrtf(squared_euclidean(query, node->vantage_point.coords, dim));
    (*evals)++;

    if (d < *best_dist) {
        *best_dist = d;
        *best_point = node->vantage_point;
    }

    float tau = *best_dist;

    /* Вибір порядку обходу та відсікання за нерівністю трикутника */
    if (d < node->threshold) {
        if (d - tau <= node->threshold) {
            vp_search_recursive(node->inside, query, dim, best_dist, best_point, evals);
        }
        if (d + tau >= node->threshold) {
            vp_search_recursive(node->outside, query, dim, best_dist, best_point, evals);
        }
    } else {
        if (d + tau >= node->threshold) {
            vp_search_recursive(node->outside, query, dim, best_dist, best_point, evals);
        }
        if (d - tau <= node->threshold) {
            vp_search_recursive(node->inside, query, dim, best_dist, best_point, evals);
        }
    }
}

void vp_free(vp_node_t *node) {
    if (!node) return;
    vp_free(node->inside);
    vp_free(node->outside);
    free(node);
}
