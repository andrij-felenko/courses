#include <stdio.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    double x;
    double y;
} Point2D;

typedef struct {
    double a, b, x_off;
    double c, d, y_off;
} AffineTransform;

static bool compute_fiducial_affine_matrix(
    const Point2D cad[3],
    const Point2D real[3],
    AffineTransform* out_tf)
{
    // Знаменник визначника матриці координат трьох точок
    double det = cad[0].x * (cad[1].y - cad[2].y) +
                 cad[1].x * (cad[2].y - cad[0].y) +
                 cad[2].x * (cad[0].y - cad[1].y);

    if (fabs(det) < 1.0e-9) {
        return false; // Точки лежать на одній прямій (вироджений трикутник)
    }

    double inv_det = 1.0 / det;

    // Розрахунок коефіцієнтів для координати X
    out_tf->a = (real[0].x * (cad[1].y - cad[2].y) +
                 real[1].x * (cad[2].y - cad[0].y) +
                 real[2].x * (cad[0].y - cad[1].y)) * inv_det;

    out_tf->b = (real[0].x * (cad[2].x - cad[1].x) +
                 real[1].x * (cad[0].x - cad[2].x) +
                 real[2].x * (cad[1].x - cad[0].x)) * inv_det;

    out_tf->x_off = (real[0].x * (cad[1].x * cad[2].y - cad[2].x * cad[1].y) +
                     real[1].x * (cad[2].x * cad[0].y - cad[0].x * cad[2].y) +
                     real[2].x * (cad[0].x * cad[1].y - cad[1].x * cad[0].y)) * inv_det;

    // Розрахунок коефіцієнтів для координати Y
    out_tf->c = (real[0].y * (cad[1].y - cad[2].y) +
                 real[1].y * (cad[2].y - cad[0].y) +
                 real[2].y * (cad[0].y - cad[1].y)) * inv_det;

    out_tf->d = (real[0].y * (cad[2].x - cad[1].x) +
                 real[1].y * (cad[0].x - cad[2].x) +
                 real[2].y * (cad[1].x - cad[0].x)) * inv_det;

    out_tf->y_off = (real[0].y * (cad[1].x * cad[2].y - cad[2].x * cad[1].y) +
                     real[1].y * (cad[2].x * cad[0].y - cad[0].x * cad[2].y) +
                     real[2].y * (cad[0].x * cad[1].y - cad[1].x * cad[0].y)) * inv_det;

    return true;
}

static Point2D transform_component_coord(const AffineTransform* tf, Point2D cad_pt) {
    Point2D real_pt;
    real_pt.x = tf->a * cad_pt.x + tf->b * cad_pt.y + tf->x_off;
    real_pt.y = tf->c * cad_pt.x + tf->d * cad_pt.y + tf->y_off;
    return real_pt;
}
