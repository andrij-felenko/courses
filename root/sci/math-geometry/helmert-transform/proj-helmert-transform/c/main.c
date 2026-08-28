#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define ARCSEC_TO_RAD (4.8481368110953599e-6)

/* Геодезичні конвенції орієнтації кутів повороту */
typedef enum {
    HELMERT_POSITION_VECTOR = 0, /* EPSG: 9606 (IERS / ISO 19111) */
    HELMERT_COORDINATE_FRAME = 1  /* EPSG: 9607 (Bursa-Wolf)      */
} HelmertConvention;

/* Тривимірний вектор декартових координат у метрах */
typedef struct {
    double x;
    double y;
    double z;
} Vec3;

/* Семипараметричний набір Гельмерта */
typedef struct {
    double tx;  /* Зсув по X, м */
    double ty;  /* Зсув по Y, м */
    double tz;  /* Зсув по Z, м */
    double rx;  /* Поворот навколо X, кутові секунди */
    double ry;  /* Поворот навколо Y, кутові секунди */
    double rz;  /* Поворот навколо Z, кутові секунди */
    double s_ppm; /* Зміна масштабу, ppm (parts per million, 10^-6) */
    HelmertConvention convention;
} Helmert7;

/* Десятипараметричний набір Молоденського — Бадекаса */
typedef struct {
    Helmert7 h7;
    Vec3 centroid; /* Координати центру обертання (X0, Y0, Z0), м */
} Helmert10;

/* Чотирнадцятипараметричний кінематичний набір (з урахуванням швидкостей) */
typedef struct {
    Helmert7 base;       /* Параметри на опорну епоху t0 */
    double dtx;          /* Швидкість зсуву X, м/рік */
    double dty;          /* Швидкість зсуву Y, м/рік */
    double dtz;          /* Швидкість зсуву Z, м/рік */
    double drx;          /* Швидкість повороту X, кутові секунди/рік */
    double dry;          /* Швидкість повороту Y, кутові секунди/рік */
    double drz;          /* Швидкість повороту Z, кутові секунди/рік */
    double ds_ppm;       /* Швидкість зміни масштабу, ppm/рік */
    double epoch_t0;     /* Опорна епоха, дробовий рік (наприклад, 2010.0) */
} Helmert14;

/* Пряме 7-параметричне перетворення */
Vec3 helmert7_forward(const Helmert7 *h, Vec3 p) {
    /* Корекція знаку кутів за конвенцією */
    double sign = (h->convention == HELMERT_COORDINATE_FRAME) ? -1.0 : 1.0;
    double rx = h->rx * ARCSEC_TO_RAD * sign;
    double ry = h->ry * ARCSEC_TO_RAD * sign;
    double rz = h->rz * ARCSEC_TO_RAD * sign;
    double s  = h->s_ppm * 1.0e-6;

    /* Матриця (1 + s) * R у лінеаризованому вигляді */
    double x_rot = (1.0 + s) * ( p.x - rz * p.y + ry * p.z);
    double y_rot = (1.0 + s) * ( rz * p.x + p.y - rx * p.z);
    double z_rot = (1.0 + s) * (-ry * p.x + rx * p.y + p.z);

    Vec3 out;
    out.x = h->tx + x_rot;
    out.y = h->ty + y_rot;
    out.z = h->tz + z_rot;
    return out;
}

/* Зворотне 7-параметричне перетворення */
Vec3 helmert7_inverse(const Helmert7 *h, Vec3 p) {
    /* Віднімаємо лінійний зсув */
    double dx = p.x - h->tx;
    double dy = p.y - h->ty;
    double dz = p.z - h->tz;

    double sign = (h->convention == HELMERT_COORDINATE_FRAME) ? -1.0 : 1.0;
    double rx = h->rx * ARCSEC_TO_RAD * sign;
    double ry = h->ry * ARCSEC_TO_RAD * sign;
    double rz = h->rz * ARCSEC_TO_RAD * sign;
    double scale = 1.0 / (1.0 + h->s_ppm * 1.0e-6);

    /* Множення на транспоновану матрицю обертання R^T */
    Vec3 out;
    out.x = scale * ( dx + rz * dy - ry * dz);
    out.y = scale * (-rz * dx + dy + rx * dz);
    out.z = scale * ( ry * dx - rx * dy + dz);
    return out;
}

/* Пряме перетворення Молоденського — Бадекаса (10 параметрів) */
Vec3 helmert10_forward(const Helmert10 *h, Vec3 p) {
    /* Зсув точки відносно центроїда */
    Vec3 p_rel;
    p_rel.x = p.x - h->centroid.x;
    p_rel.y = p.y - h->centroid.y;
    p_rel.z = p.z - h->centroid.z;

    double sign = (h->h7.convention == HELMERT_COORDINATE_FRAME) ? -1.0 : 1.0;
    double rx = h->h7.rx * ARCSEC_TO_RAD * sign;
    double ry = h->h7.ry * ARCSEC_TO_RAD * sign;
    double rz = h->h7.rz * ARCSEC_TO_RAD * sign;
    double s  = h->h7.s_ppm * 1.0e-6;

    double x_rot = (1.0 + s) * ( p_rel.x - rz * p_rel.y + ry * p_rel.z);
    double y_rot = (1.0 + s) * ( rz * p_rel.x + p_rel.y - rx * p_rel.z);
    double z_rot = (1.0 + s) * (-ry * p_rel.x + rx * p_rel.y + p_rel.z);

    Vec3 out;
    out.x = h->centroid.x + h->h7.tx + x_rot;
    out.y = h->centroid.y + h->h7.ty + y_rot;
    out.z = h->centroid.z + h->h7.tz + z_rot;
    return out;
}

/* Обчислення миттєвих параметрів на епоху t для 14-параметричної моделі */
Helmert7 helmert14_at_epoch(const Helmert14 *h14, double epoch_t) {
    double dt = epoch_t - h14->epoch_t0;
    Helmert7 h;
    h.tx    = h14->base.tx    + h14->dtx * dt;
    h.ty    = h14->base.ty    + h14->dty * dt;
    h.tz    = h14->base.tz    + h14->dtz * dt;
    h.rx    = h14->base.rx    + h14->drx * dt;
    h.ry    = h14->base.ry    + h14->dry * dt;
    h.rz    = h14->base.rz    + h14->drz * dt;
    h.s_ppm = h14->base.s_ppm + h14->ds_ppm * dt;
    h.convention = h14->base.convention;
    return h;
}

/* Оцінка 7 параметрів Гельмерта за методом найменших квадратів */
bool estimate_helmert7(const Vec3 *src, const Vec3 *tgt, int n,
                       HelmertConvention convention, Helmert7 *out_h) {
    if (n < 3) return false;

    /* Матриця нормальних рівнянь N = A^T * A (7x7) та вектор U = A^T * L (7x1) */
    double N[7][7] = {0};
    double U[7] = {0};

    for (int i = 0; i < n; ++i) {
        double x = src[i].x;
        double y = src[i].y;
        double z = src[i].z;

        double lx = tgt[i].x - x;
        double ly = tgt[i].y - y;
        double lz = tgt[i].z - z;

        /* Рядки матриці спостережень A для точки i (для Position Vector) */
        /* Рядок 1: [ 1,  0,  0,    0,   z,  -y,  x ] */
        /* Рядок 2: [ 0,  1,  0,   -z,   0,   x,  y ] */
        /* Рядок 3: [ 0,  0,  1,    y,  -x,   0,  z ] */
        double A[3][7] = {
            { 1.0, 0.0, 0.0,  0.0 * ARCSEC_TO_RAD,  z * ARCSEC_TO_RAD, -y * ARCSEC_TO_RAD, x * 1.0e-6 },
            { 0.0, 1.0, 0.0, -z * ARCSEC_TO_RAD,  0.0 * ARCSEC_TO_RAD,  x * ARCSEC_TO_RAD, y * 1.0e-6 },
            { 0.0, 0.0, 1.0,  y * ARCSEC_TO_RAD, -x * ARCSEC_TO_RAD,  0.0 * ARCSEC_TO_RAD, z * 1.0e-6 }
        };

        if (convention == HELMERT_COORDINATE_FRAME) {
            for (int r = 0; r < 3; ++r) {
                A[r][3] = -A[r][3];
                A[r][4] = -A[r][4];
                A[r][5] = -A[r][5];
            }
        }

        double L[3] = { lx, ly, lz };

        /* Акумуляція N = A^T * A та U = A^T * L */
        for (int j = 0; j < 7; ++j) {
            for (int k = 0; k < 7; ++k) {
                for (int r = 0; r < 3; ++r) {
                    N[j][k] += A[r][j] * A[r][k];
                }
            }
            for (int r = 0; r < 3; ++r) {
                U[j] += A[r][j] * L[r];
            }
        }
    }

    /* Розв'язання системи N * x = U методом виключення Гауса з вибором головного елемента */
    double Aug[7][8];
    for (int i = 0; i < 7; ++i) {
        for (int j = 0; j < 7; ++j) Aug[i][j] = N[i][j];
        Aug[i][7] = U[i];
    }

    for (int col = 0; col < 7; ++col) {
        int pivot = col;
        double max_val = fabs(Aug[col][col]);
        for (int r = col + 1; r < 7; ++r) {
            if (fabs(Aug[r][col]) > max_val) {
                max_val = fabs(Aug[r][col]);
                pivot = r;
            }
        }
        if (max_val < 1e-15) return false; /* Матриця вироджена */

        if (pivot != col) {
            for (int k = col; k < 8; ++k) {
                double tmp = Aug[col][k];
                Aug[col][k] = Aug[pivot][k];
                Aug[pivot][k] = tmp;
            }
        }

        for (int r = col + 1; r < 7; ++r) {
            double factor = Aug[r][col] / Aug[col][col];
            for (int k = col; k < 8; ++k) {
                Aug[r][k] -= factor * Aug[col][k];
            }
        }
    }

    double sol[7];
    for (int r = 6; r >= 0; --r) {
        double sum = Aug[r][7];
        for (int k = r + 1; k < 7; ++k) {
            sum -= Aug[r][k] * sol[k];
        }
        sol[r] = sum / Aug[r][r];
    }

    out_h->tx = sol[0];
    out_h->ty = sol[1];
    out_h->tz = sol[2];
    out_h->rx = sol[3];
    out_h->ry = sol[4];
    out_h->rz = sol[5];
    out_h->s_ppm = sol[6];
    out_h->convention = convention;
    return true;
}

int main(void) {
    /* Тестовий набір EPSG:1618 (ED50 до WGS 84 для Великої Британії) */
    Helmert7 ed50_to_wgs84 = {
        .tx = -89.5,
        .ty = -93.8,
        .tz = -123.1,
        .rx = 0.0,
        .ry = 0.0,
        .rz = -0.156,
        .s_ppm = -1.2,
        .convention = HELMERT_POSITION_VECTOR
    };

    Vec3 pt_ed50 = { 3978280.0, -100410.0, 4968390.0 };
    Vec3 pt_wgs84 = helmert7_forward(&ed50_to_wgs84, pt_ed50);
    Vec3 pt_back  = helmert7_inverse(&ed50_to_wgs84, pt_wgs84);

    printf("Пряме перетворення ED50 -> WGS84:\n");
    printf("  X: %12.3f -> %12.3f м\n", pt_ed50.x, pt_wgs84.x);
    printf("  Y: %12.3f -> %12.3f м\n", pt_ed50.y, pt_wgs84.y);
    printf("  Z: %12.3f -> %12.3f м\n", pt_ed50.z, pt_wgs84.z);

    printf("\nНев'язка зворотного перетворення:\n");
    printf("  dX: %.6f мм, dY: %.6f мм, dZ: %.6f мм\n",
           (pt_back.x - pt_ed50.x) * 1000.0,
           (pt_back.y - pt_ed50.y) * 1000.0,
           (pt_back.z - pt_ed50.z) * 1000.0);

    return 0;
}
