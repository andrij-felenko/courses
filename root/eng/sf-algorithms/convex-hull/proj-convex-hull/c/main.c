#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    int64_t x;
    int64_t y;
} Point;

/* Векторний косий добуток векторів (B - A) та (C - A).
   Повертає:
   > 0: поворот ліворуч (CCW)
   < 0: поворот праворуч (CW)
   = 0: точки колінеарні */
static inline int64_t cross_product(Point a, Point b, Point c) {
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
}

/* Лексикографічний компаратор для qsort: спочатку за X, потім за Y */
static int compare_points(const void *pa, const void *pb) {
    const Point *a = (const Point *)pa;
    const Point *b = (const Point *)pb;
    if (a->x != b->x) {
        return (a->x < b->x) ? -1 : 1;
    }
    if (a->y != b->y) {
        return (a->y < b->y) ? -1 : 1;
    }
    return 0;
}

/* Видалення послідовних дублікатів після сортування */
static size_t remove_duplicates(Point *pts, size_t n) {
    if (n <= 1) return n;
    size_t unique_count = 1;
    for (size_t i = 1; i < n; i++) {
        if (pts[i].x != pts[unique_count - 1].x || pts[i].y != pts[unique_count - 1].y) {
            pts[unique_count++] = pts[i];
        }
    }
    return unique_count;
}

/* Побудова строгої опуклої оболонки (без проміжних колінеарних точок).
   Повертає кількість вершин у результуючому масиві hull.
   Викликач виділяє масив hull місткістю щонайменше 2 * n елементів. */
size_t convex_hull_andrew(Point *pts, size_t n, Point *hull) {
    if (n <= 2) {
        for (size_t i = 0; i < n; i++) {
            hull[i] = pts[i];
        }
        return n;
    }

    /* 1. Лексикографічне сортування */
    qsort(pts, n, sizeof(Point), compare_points);
    n = remove_duplicates(pts, n);

    if (n <= 2) {
        for (size_t i = 0; i < n; i++) {
            hull[i] = pts[i];
        }
        return n;
    }

    size_t k = 0;

    /* 2. Побудова нижньої оболонки (зліва направо) */
    for (size_t i = 0; i < n; i++) {
        while (k >= 2 && cross_product(hull[k - 2], hull[k - 1], pts[i]) <= 0) {
            k--;
        }
        hull[k++] = pts[i];
    }

    /* 3. Побудова верхньої оболонки (справа наліво) */
    size_t lower_limit = k + 1;
    for (size_t i = n - 1; i > 0; i--) {
        size_t idx = i - 1;
        while (k >= lower_limit && cross_product(hull[k - 2], hull[k - 1], pts[idx]) <= 0) {
            k--;
        }
        hull[k++] = pts[idx];
    }

    /* Остання додана точка збігається з hull[0], тому зменшуємо розмір на 1 */
    k--;
    return k;
}
