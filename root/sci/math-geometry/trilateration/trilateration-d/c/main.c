#include <stdio.h>
#include <stdbool.h>
#include <math.h>

/* Тривимірний вектор та координатна точка */
typedef struct {
    double x;
    double y;
    double z;
} Vec3;

/* Опорний маяк: просторові координати та виміряна відстань */
typedef struct {
    Vec3 pos;
    double distance;
} Anchor;

/* Результат розрахунку позиції */
typedef struct {
    Vec3 position;
    double residual_norm;
    bool success;
} TrilaterationResult;

/* Обчислення визначника квадратної матриці 3x3 */
static double mat3_det(const double m[3][3]) {
    return m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) -
           m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) +
           m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]);
}

/* Обчислення оберненої матриці 3x3 через матрицю алгебраїчних доповнень */
static bool mat3_inverse(const double m[3][3], double inv[3][3]) {
    double det = mat3_det(m);
    if (fabs(det) < 1e-12) {
        return false; /* Матриця сингулярна або погано обумовлена */
    }

    double inv_det = 1.0 / det;
    inv[0][0] =  (m[1][1] * m[2][2] - m[1][2] * m[2][1]) * inv_det;
    inv[0][1] = -(m[0][1] * m[2][2] - m[0][2] * m[2][1]) * inv_det;
    inv[0][2] =  (m[0][1] * m[1][2] - m[0][2] * m[1][1]) * inv_det;

    inv[1][0] = -(m[1][0] * m[2][2] - m[1][2] * m[2][0]) * inv_det;
    inv[1][1] =  (m[0][0] * m[2][2] - m[0][2] * m[2][0]) * inv_det;
    inv[1][2] = -(m[0][0] * m[1][2] - m[0][2] * m[1][0]) * inv_det;

    inv[2][0] =  (m[1][0] * m[2][1] - m[1][1] * m[2][0]) * inv_det;
    inv[2][1] = -(m[0][0] * m[2][1] - m[0][1] * m[2][0]) * inv_det;
    inv[2][2] =  (m[0][0] * m[1][1] - m[0][1] * m[1][0]) * inv_det;

    return true;
}

/*
 * 3D трилатерація методом лінеаризованих найменших квадратів.
 * anchors: масив опорних станцій із координатами та виміряними відстанями
 * count: кількість маяків (повинно бути >= 4)
 */
TrilaterationResult trilaterate_3d_least_squares(const Anchor* anchors, size_t count) {
    TrilaterationResult res = { .position = {0, 0, 0}, .residual_norm = 0.0, .success = false };
    if (!anchors || count < 4) {
        return res;
    }

    /* Базовий маяк: індекс 0 */
    double x1 = anchors[0].pos.x;
    double y1 = anchors[0].pos.y;
    double z1 = anchors[0].pos.z;
    double r1 = anchors[0].distance;
    double k1 = x1 * x1 + y1 * y1 + z1 * z1;

    /* Формуємо нормальні рівняння A^T * A * X = A^T * b без збереження повної матриці A */
    double AtA[3][3] = { {0, 0, 0}, {0, 0, 0}, {0, 0, 0} };
    double Atb[3] = { 0, 0, 0 };

    for (size_t i = 1; i < count; ++i) {
        double xi = anchors[i].pos.x;
        double yi = anchors[i].pos.y;
        double zi = anchors[i].pos.z;
        double ri = anchors[i].distance;
        double ki = xi * xi + yi * yi + zi * zi;

        /* Рядок матриці A: A_row = [ 2(xi - x1), 2(yi - y1), 2(zi - z1) ] */
        double row[3] = {
            2.0 * (xi - x1),
            2.0 * (yi - y1),
            2.0 * (zi - z1)
        };

        /* Елемент вектора b: r1^2 - ri^2 + ki - k1 */
        double b_val = (r1 * r1 - ri * ri) + (ki - k1);

        /* Накопичуємо AtA += row^T * row */
        for (int r = 0; r < 3; ++r) {
            for (int c = 0; c < 3; ++c) {
                AtA[r][c] += row[r] * row[c];
            }
            /* Накопичуємо Atb += row^T * b_val */
            Atb[r] += row[r] * b_val;
        }
    }

    /* Обертаємо матрицю нормальних рівнянь (AtA)^-1 */
    double inv_AtA[3][3];
    if (!mat3_inverse(AtA, inv_AtA)) {
        return res; /* Матриця вироджена: маяки компланарні або колінеарні */
    }

    /* Обчислюємо X = (AtA)^-1 * Atb */
    res.position.x = inv_AtA[0][0] * Atb[0] + inv_AtA[0][1] * Atb[1] + inv_AtA[0][2] * Atb[2];
    res.position.y = inv_AtA[1][0] * Atb[0] + inv_AtA[1][0] * Atb[1] + inv_AtA[1][2] * Atb[2];
    res.position.z = inv_AtA[2][0] * Atb[0] + inv_AtA[2][1] * Atb[1] + inv_AtA[2][2] * Atb[2];

    /* Розрахунок середньоквадратичної нев'язки за всіма маяками */
    double sum_sq_err = 0.0;
    for (size_t i = 0; i < count; ++i) {
        double dx = res.position.x - anchors[i].pos.x;
        double dy = res.position.y - anchors[i].pos.y;
        double dz = res.position.z - anchors[i].pos.z;
        double estimated_dist = sqrt(dx * dx + dy * dy + dz * dz);
        double err = estimated_dist - anchors[i].distance;
        sum_sq_err += err * err;
    }
    res.residual_norm = sqrt(sum_sq_err / (double)count);
    res.success = true;

    return res;
}
