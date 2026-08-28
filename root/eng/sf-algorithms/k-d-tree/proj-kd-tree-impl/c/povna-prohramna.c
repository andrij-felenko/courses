#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <float.h>

#define K_DIM 2

typedef struct {
    double coords[K_DIM];
    int id;
} Point;

typedef struct KDNode {
    Point point;
    struct KDNode* left;
    struct KDNode* right;
} KDNode;

typedef struct {
    KDNode* root;
    KDNode* node_pool;
    size_t pool_capacity;
    size_t pool_size;
} KDTree;

/* Квадрат евклідової відстані між двома точками */
static inline double distance_squared(const Point* a, const Point* b) {
    double sum = 0.0;
    for (int i = 0; i < K_DIM; ++i) {
        double diff = a->coords[i] - b->coords[i];
        sum += diff * diff;
    }
    return sum;
}

/* Обмін двох точок у масиві */
static void swap_points(Point* a, Point* b) {
    Point tmp = *a;
    *a = *b;
    *b = tmp;
}

/* Двостороннє розбиття Хоара за координатою d */
static size_t partition(Point* pts, size_t left, size_t right, size_t pivot_idx, int d) {
    double pivot_val = pts[pivot_idx].coords[d];
    swap_points(&pts[pivot_idx], &pts[right]);
    size_t store_idx = left;
    for (size_t i = left; i < right; ++i) {
        if (pts[i].coords[d] < pivot_val) {
            swap_points(&pts[i], &pts[store_idx]);
            store_idx++;
        }
    }
    swap_points(&pts[store_idx], &pts[right]);
    return store_idx;
}

/* Знаходження k-ї порядкової статистики за лінійний час O(N) */
static void quickselect(Point* pts, size_t left, size_t right, size_t k, int d) {
    while (left < right) {
        size_t pivot_idx = left + (right - left) / 2;
        size_t new_pivot = partition(pts, left, right, pivot_idx, d);
        if (k == new_pivot) {
            return;
        } else if (k < new_pivot) {
            if (new_pivot == 0) return;
            right = new_pivot - 1;
        } else {
            left = new_pivot + 1;
        }
    }
}

/* Рекурсивна побудова збалансованого K-d дерева за O(N log N) */
static KDNode* build_recursive(KDTree* tree, Point* pts, size_t left, size_t right, int depth) {
    if (left > right) return NULL;

    size_t mid = left + (right - left) / 2;
    int d = depth % K_DIM;

    quickselect(pts, left, right, mid, d);

    KDNode* node = &tree->node_pool[tree->pool_size++];
    node->point = pts[mid];
    node->left = NULL;
    node->right = NULL;

    if (mid > left) {
        node->left = build_recursive(tree, pts, left, mid - 1, depth + 1);
    }
    if (mid < right) {
        node->right = build_recursive(tree, pts, mid + 1, right, depth + 1);
    }

    return node;
}

KDTree* kdtree_create(Point* pts, size_t n) {
    KDTree* tree = (KDTree*)malloc(sizeof(KDTree));
    if (!tree) return NULL;

    tree->pool_capacity = n;
    tree->pool_size = 0;
    tree->node_pool = (KDNode*)malloc(sizeof(KDNode) * n);
    if (!tree->node_pool) {
        free(tree);
        return NULL;
    }

    if (n > 0 && pts != NULL) {
        tree->root = build_recursive(tree, pts, 0, n - 1, 0);
    } else {
        tree->root = NULL;
    }

    return tree;
}

void kdtree_free(KDTree* tree) {
    if (!tree) return;
    if (tree->node_pool) free(tree->node_pool);
    free(tree);
}

/* Пошук найближчого сусіда (NNS) із відсіканням гілок за евклідовою відстанню */
static void nn_search_recursive(const KDNode* node, const Point* target, int depth,
                                const Point** best_point, double* best_dist_sq) {
    if (!node) return;

    double d_sq = distance_squared(&node->point, target);
    if (d_sq < *best_dist_sq) {
        *best_dist_sq = d_sq;
        *best_point = &node->point;
    }

    int d = depth % K_DIM;
    double diff = target->coords[d] - node->point.coords[d];
    double diff_sq = diff * diff;

    const KDNode* near_child = (diff <= 0.0) ? node->left : node->right;
    const KDNode* far_child  = (diff <= 0.0) ? node->right : node->left;

    /* 1. Пріоритетний спуск у ближче піддерево */
    nn_search_recursive(near_child, target, depth + 1, best_point, best_dist_sq);

    /* 2. Геометричне відсікання: перевірка перетину сфери кандидата з площиною */
    if (diff_sq < *best_dist_sq) {
        nn_search_recursive(far_child, target, depth + 1, best_point, best_dist_sq);
    }
}

const Point* kdtree_nearest_neighbor(const KDTree* tree, const Point* target, double* out_dist_sq) {
    if (!tree || !tree->root) return NULL;
    const Point* best_point = NULL;
    double best_dist_sq = DBL_MAX;

    nn_search_recursive(tree->root, target, 0, &best_point, &best_dist_sq);

    if (out_dist_sq) *out_dist_sq = best_dist_sq;
    return best_point;
}

/* Ортогональний діапазонний пошук */
static void range_search_recursive(const KDNode* node, const Point* min_pt, const Point* max_pt,
                                   int depth, Point* results, size_t* result_count, size_t max_results) {
    if (!node || *result_count >= max_results) return;

    bool inside = true;
    for (int i = 0; i < K_DIM; ++i) {
        if (node->point.coords[i] < min_pt->coords[i] || node->point.coords[i] > max_pt->coords[i]) {
            inside = false;
            break;
        }
    }
    if (inside) {
        results[(*result_count)++] = node->point;
    }

    int d = depth % K_DIM;
    if (node->point.coords[d] >= min_pt->coords[d]) {
        range_search_recursive(node->left, min_pt, max_pt, depth + 1, results, result_count, max_results);
    }
    if (node->point.coords[d] <= max_pt->coords[d]) {
        range_search_recursive(node->right, min_pt, max_pt, depth + 1, results, result_count, max_results);
    }
}

size_t kdtree_range_query(const KDTree* tree, const Point* min_pt, const Point* max_pt,
                          Point* out_results, size_t max_results) {
    if (!tree || !tree->root) return 0;
    size_t count = 0;
    range_search_recursive(tree->root, min_pt, max_pt, 0, out_results, &count, max_results);
    return count;
}
