#include <stdio.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    double x;
    double y;
} Point2D;

typedef struct {
    int v[3]; /* Індекси вершин у масиві точок */
} Triangle;

/* Предикат 2D-орієнтації (подвійна площа трикутника abc):
   > 0 : поворот ліворуч (проти годинникової стрілки, CCW)
   < 0 : поворот праворуч (за годинниковою стрілкою, CW)
   = 0 : точки лежать на одній прямій (колінеарні) */
double orient2d(Point2D a, Point2D b, Point2D c) {
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
}

/* Предикат InCircle: перевірка потрапляння точки d у коло трикутника abc */
double incircle(Point2D a, Point2D b, Point2D c, Point2D d) {
    /* Якщо abc орієнтований CW, міняємо місцями b та c для збереження знаку */
    if (orient2d(a, b, c) < 0.0) {
        Point2D tmp = b;
        b = c;
        c = tmp;
    }

    double adx = a.x - d.x, ady = a.y - d.y;
    double bdx = b.x - d.x, bdy = b.y - d.y;
    double cdx = c.x - d.x, cdy = c.y - d.y;

    double ab_det = adx * bdy - ady * bdx;
    double bc_det = bdx * cdy - bdy * cdx;
    double ca_det = cdx * ady - cdy * adx;

    double alift = adx * adx + ady * ady;
    double blift = bdx * bdx + bdy * bdy;
    double clift = cdx * cdx + cdy * cdy;

    return alift * bc_det + blift * ca_det + clift * ab_det;
}

/* Перевірка легальності ребра між трикутником (a, b, c) та четвертою вершиною d:
   true  - ребро легальне (коло порожнє)
   false - ребро нелегальне, потрібен фліп */
bool is_edge_legal(Point2D a, Point2D b, Point2D c, Point2D d) {
    return incircle(a, b, c, d) <= 1e-12;
}
