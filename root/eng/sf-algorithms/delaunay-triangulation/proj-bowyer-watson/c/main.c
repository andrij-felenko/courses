#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    double x;
    double y;
} Point2D;

typedef struct {
    Point2D a;
    Point2D b;
} Edge2D;

typedef struct {
    Point2D a;
    Point2D b;
    Point2D c;
} Triangle2D;

/* Перевірка збігу двох точок із числовою точністю */
static inline bool point_equals(Point2D p1, Point2D p2) {
    return fabs(p1.x - p2.x) < 1e-9 && fabs(p1.y - p2.y) < 1e-9;
}

/* Перевірка збігу двох ребер без урахування напрямку */
static inline bool edge_equals(Edge2D e1, Edge2D e2) {
    return (point_equals(e1.a, e2.a) && point_equals(e1.b, e2.b)) ||
           (point_equals(e1.a, e2.b) && point_equals(e1.b, e2.a));
}

/* Перевірка, чи містить трикутник задану вершину */
static inline bool triangle_has_vertex(Triangle2D t, Point2D p) {
    return point_equals(t.a, p) || point_equals(t.b, p) || point_equals(t.c, p);
}

/* Орієнтований подвійний трикутник (CCW > 0) */
static inline double orientation_ccw(Point2D a, Point2D b, Point2D c) {
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
}

/* Предикат InCircle: чи лежить точка d всередині описаного кола трикутника abc */
bool in_circumcircle(Point2D a, Point2D b, Point2D c, Point2D d) {
    /* Якщо трикутник орієнтований CW, міняємо місцями b та c */
    if (orientation_ccw(a, b, c) < 0.0) {
        Point2D tmp = b;
        b = c;
        c = tmp;
    }

    double adx = a.x - d.x;
    double ady = a.y - d.y;
    double bdx = b.x - d.x;
    double bdy = b.y - d.y;
    double cdx = c.x - d.x;
    double cdy = c.y - d.y;

    double ab_det = adx * bdy - ady * bdx;
    double bc_det = bdx * cdy - bdy * cdx;
    double ca_det = cdx * ady - cdy * adx;

    double alift = adx * adx + ady * ady;
    double blift = bdx * bdx + bdy * bdy;
    double clift = cdx * cdx + cdy * cdy;

    double det = alift * bc_det + blift * ca_det + clift * ab_det;
    return det > 1e-12;
}

/* Динамічний масив трикутників */
typedef struct {
    Triangle2D* data;
    size_t size;
    size_t capacity;
} TriangleVector;

static void tri_vector_init(TriangleVector* v, size_t cap) {
    v->data = (Triangle2D*)malloc(cap * sizeof(Triangle2D));
    v->size = 0;
    v->capacity = cap;
}

static void tri_vector_push(TriangleVector* v, Triangle2D t) {
    if (v->size >= v->capacity) {
        v->capacity = v->capacity == 0 ? 8 : v->capacity * 2;
        v->data = (Triangle2D*)realloc(v->data, v->capacity * sizeof(Triangle2D));
    }
    v->data[v->size++] = t;
}

static void tri_vector_free(TriangleVector* v) {
    free(v->data);
    v->data = NULL;
    v->size = v->capacity = 0;
}

/* Інкрементний алгоритм Бойєра-Ватсона */
TriangleVector bowyer_watson(const Point2D* points, size_t n) {
    TriangleVector mesh;
    tri_vector_init(&mesh, 16);
    if (n == 0) return mesh;

    /* Обчислення Bounding Box */
    double min_x = points[0].x, max_x = points[0].x;
    double min_y = points[0].y, max_y = points[0].y;
    for (size_t i = 1; i < n; ++i) {
        if (points[i].x < min_x) min_x = points[i].x;
        if (points[i].x > max_x) max_x = points[i].x;
        if (points[i].y < min_y) min_y = points[i].y;
        if (points[i].y > max_y) max_y = points[i].y;
    }

    double dx = max_x - min_x;
    double dy = max_y - min_y;
    double delta_max = (dx > dy ? dx : dy) * 20.0;
    if (delta_max < 1e-5) delta_max = 100.0;
    double mid_x = (min_x + max_x) * 0.5;
    double mid_y = (min_y + max_y) * 0.5;

    /* Побудова супертрикутника */
    Point2D st_a = { mid_x - delta_max, mid_y - delta_max };
    Point2D st_b = { mid_x + delta_max, mid_y - delta_max };
    Point2D st_c = { mid_x, mid_y + delta_max };
    Triangle2D super_tri = { st_a, st_b, st_c };

    tri_vector_push(&mesh, super_tri);

    /* Тимчасові буфери для полігональної порожнини */
    Edge2D* polygon = (Edge2D*)malloc(1024 * sizeof(Edge2D));
    size_t poly_capacity = 1024;

    for (size_t p_idx = 0; p_idx < n; ++p_idx) {
        Point2D pt = points[p_idx];
        size_t poly_size = 0;

        /* Знаходимо недійсні трикутники та збираємо їхні ребра */
        size_t write_idx = 0;
        for (size_t i = 0; i < mesh.size; ++i) {
            Triangle2D cur_t = mesh.data[i];
            if (in_circumcircle(cur_t.a, cur_t.b, cur_t.c, pt)) {
                Edge2D e[3] = {
                    { cur_t.a, cur_t.b },
                    { cur_t.b, cur_t.c },
                    { cur_t.c, cur_t.a }
                };
                for (int j = 0; j < 3; ++j) {
                    if (poly_size >= poly_capacity) {
                        poly_capacity *= 2;
                        polygon = (Edge2D*)realloc(polygon, poly_capacity * sizeof(Edge2D));
                    }
                    polygon[poly_size++] = e[j];
                }
            } else {
                mesh.data[write_idx++] = cur_t;
            }
        }
        mesh.size = write_idx;

        /* Знаходимо унікальні межові ребра (що з'явилися рівно один раз) */
        for (size_t i = 0; i < poly_size; ++i) {
            bool is_shared = false;
            for (size_t j = 0; j < poly_size; ++j) {
                if (i != j && edge_equals(polygon[i], polygon[j])) {
                    is_shared = true;
                    break;
                }
            }
            if (!is_shared) {
                Triangle2D new_t = { polygon[i].a, polygon[i].b, pt };
                tri_vector_push(&mesh, new_t);
            }
        }
    }

    free(polygon);

    /* Видалення трикутників, пов'язаних із супертрикутником */
    size_t final_size = 0;
    for (size_t i = 0; i < mesh.size; ++i) {
        Triangle2D t = mesh.data[i];
        if (!triangle_has_vertex(t, st_a) &&
            !triangle_has_vertex(t, st_b) &&
            !triangle_has_vertex(t, st_c)) {
            mesh.data[final_size++] = t;
        }
    }
    mesh.size = final_size;
    return mesh;
}
