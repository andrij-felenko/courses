#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>
#include <string.h>

#define DIM 3
#define LEAF_CAPACITY 2

typedef struct {
    double coords[DIM];
    int id;
} Point;

typedef struct {
    Point point;
    double dist;
} Neighbor;

/* Обмежена максимальна купа (Max-Heap) для збереження k найближчих кандидатів */
typedef struct {
    Neighbor *data;
    int size;
    int capacity;
} MaxHeap;

static void heap_init(MaxHeap *h, int capacity) {
    h->data = (Neighbor *)malloc(sizeof(Neighbor) * (capacity + 1));
    h->size = 0;
    h->capacity = capacity;
}

static void heap_free(MaxHeap *h) {
    free(h->data);
}

static void heap_swap(Neighbor *a, Neighbor *b) {
    Neighbor tmp = *a;
    *a = *b;
    *b = tmp;
}

static void heap_push(MaxHeap *h, Point pt, double dist) {
    if (h->size < h->capacity) {
        int i = ++h->size;
        h->data[i].point = pt;
        h->data[i].dist = dist;
        while (i > 1 && h->data[i].dist > h->data[i / 2].dist) {
            heap_swap(&h->data[i], &h->data[i / 2]);
            i /= 2;
        }
    } else if (dist < h->data[1].dist) {
        h->data[1].point = pt;
        h->data[1].dist = dist;
        int i = 1;
        while (2 * i <= h->size) {
            int child = 2 * i;
            if (child + 1 <= h->size && h->data[child + 1].dist > h->data[child].dist) {
                child++;
            }
            if (h->data[i].dist >= h->data[child].dist) break;
            heap_swap(&h->data[i], &h->data[child]);
            i = child;
        }
    }
}

static double heap_max_dist(const MaxHeap *h) {
    return (h->size < h->capacity) ? INFINITY : h->data[1].dist;
}

/* Евклідова відстань між точками */
static double distance(const Point *a, const Point *b) {
    double sum = 0.0;
    for (int i = 0; i < DIM; ++i) {
        double diff = a->coords[i] - b->coords[i];
        sum += diff * diff;
    }
    return sqrt(sum);
}

/* Структура вузла Ball Tree */
typedef struct BallNode {
    Point center;
    double radius;
    struct BallNode *left;
    struct BallNode *right;
    Point *points;
    int num_points;
    bool is_leaf;
} BallNode;

/* Обчислення центроїда та радіуса сферичної оболонки */
static void compute_bounding_ball(BallNode *node, Point *pts, int n) {
    for (int d = 0; d < DIM; ++d) {
        double sum = 0.0;
        for (int i = 0; i < n; ++i) {
            sum += pts[i].coords[d];
        }
        node->center.coords[d] = sum / n;
    }
    node->center.id = -1;

    double max_r = 0.0;
    for (int i = 0; i < n; ++i) {
        double d = distance(&node->center, &pts[i]);
        if (d > max_r) max_r = d;
    }
    node->radius = max_r;
}

/* Побудова Ball Tree */
BallNode *ball_tree_build(Point *pts, int n) {
    if (n <= 0) return NULL;

    BallNode *node = (BallNode *)calloc(1, sizeof(BallNode));
    compute_bounding_ball(node, pts, n);

    if (n <= LEAF_CAPACITY) {
        node->is_leaf = true;
        node->num_points = n;
        node->points = (Point *)malloc(sizeof(Point) * n);
        memcpy(node->points, pts, sizeof(Point) * n);
        return node;
    }

    /* Знаходження двох найвіддаленіших опорних точок (півотів) A та B */
    int pivot_a = 0;
    double max_d = -1.0;
    for (int i = 1; i < n; ++i) {
        double d = distance(&pts[0], &pts[i]);
        if (d > max_d) { max_d = d; pivot_a = i; }
    }

    int pivot_b = pivot_a;
    max_d = -1.0;
    for (int i = 0; i < n; ++i) {
        double d = distance(&pts[pivot_a], &pts[i]);
        if (d > max_d) { max_d = d; pivot_b = i; }
    }

    /* Розбиття точок: ближчі до A йдуть ліворуч, ближчі до B — праворуч */
    int left_count = 0;
    Point *temp = (Point *)malloc(sizeof(Point) * n);
    int l_idx = 0, r_idx = n - 1;

    for (int i = 0; i < n; ++i) {
        double da = distance(&pts[i], &pts[pivot_a]);
        double db = distance(&pts[i], &pts[pivot_b]);
        if (da <= db) {
            temp[l_idx++] = pts[i];
            left_count++;
        } else {
            temp[r_idx--] = pts[i];
        }
    }

    /* Запобігання виродженому розбиттю, якщо всі точки збігаються */
    if (left_count == 0 || left_count == n) {
        left_count = n / 2;
    }

    node->left = ball_tree_build(temp, left_count);
    node->right = ball_tree_build(temp + left_count, n - left_count);
    free(temp);

    return node;
}

/* Рекурсивний пошук k-NN з відсіканням гілок за нерівністю трикутника */
void ball_tree_knn(const BallNode *node, const Point *query, MaxHeap *heap) {
    if (!node) return;

    double d_center = distance(query, &node->center);
    double d_min = d_center - node->radius;
    if (d_min < 0.0) d_min = 0.0;

    /* Відсікання гілки: якщо навіть найближчий край кулі далі за k-го сусіда */
    if (d_min >= heap_max_dist(heap)) {
        return;
    }

    if (node->is_leaf) {
        for (int i = 0; i < node->num_points; ++i) {
            double d = distance(query, &node->points[i]);
            heap_push(heap, node->points[i], d);
        }
        return;
    }

    /* Вибір пріоритетного піддерева (спуск у ближчу кулю) */
    double d_left = node->left ? distance(query, &node->left->center) : INFINITY;
    double d_right = node->right ? distance(query, &node->right->center) : INFINITY;

    if (d_left < d_right) {
        ball_tree_knn(node->left, query, heap);
        ball_tree_knn(node->right, query, heap);
    } else {
        ball_tree_knn(node->right, query, heap);
        ball_tree_knn(node->left, query, heap);
    }
}

void ball_tree_free(BallNode *node) {
    if (!node) return;
    if (node->is_leaf) {
        free(node->points);
    } else {
        ball_tree_free(node->left);
        ball_tree_free(node->right);
    }
    free(node);
}

int main(void) {
    Point pts[] = {
        {{1.0, 2.0, 3.0}, 1},
        {{1.1, 2.1, 2.9}, 2},
        {{5.0, 6.0, 7.0}, 3},
        {{5.2, 5.9, 7.1}, 4},
        {{8.0, 9.0, 1.0}, 5},
        {{1.2, 1.9, 3.1}, 6},
        {{5.1, 6.2, 6.8}, 7}
    };
    int n = sizeof(pts) / sizeof(pts[0]);
    int k = 3;

    BallNode *root = ball_tree_build(pts, n);

    Point query = {{1.05, 2.05, 3.0}, 0};
    MaxHeap heap;
    heap_init(&heap, k);

    ball_tree_knn(root, &query, &heap);

    printf("Результати точного 3-NN пошуку для запиту (1.05, 2.05, 3.0):\n");
    for (int i = 1; i <= heap.size; ++i) {
        printf("  Сусід ID=%d, coords=(%.1f, %.1f, %.1f), dist=%.4f\n",
               heap.data[i].point.id,
               heap.data[i].point.coords[0],
               heap.data[i].point.coords[1],
               heap.data[i].point.coords[2],
               heap.data[i].dist);
    }

    heap_free(&heap);
    ball_tree_free(root);
    return 0;
}
