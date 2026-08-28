#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Двовимірний вектор напруженості або позиції */
typedef struct {
    double x;
    double y;
} Vector2D;

/* Вказівник на функцію векторного поля */
typedef Vector2D (*FieldFunc)(double x, double y);

/* Модель 1: Консервативне кулонівське поле точкового заряду */
Vector2D field_coulomb(double x, double y) {
    double r2 = x * x + y * y;
    /* Регуляризація для запобігання ділення на нуль біля особливості */
    if (r2 < 1e-12) {
        r2 = 1e-12;
    }
    double r3 = r2 * sqrt(r2);
    Vector2D e;
    e.x = x / r3;
    e.y = y / r3;
    return e;
}

/* Модель 2: Вихорове електричне поле з ротором alpha = 3.0 */
Vector2D field_vortex(double x, double y) {
    double alpha = 3.0;
    Vector2D e;
    e.x = -0.5 * alpha * y;
    e.y =  0.5 * alpha * x;
    return e;
}

/* Алгоритм обчислення циркуляції по колу трапецієдальним методом */
double compute_circulation(FieldFunc field, double center_x, double center_y,
                           double radius, int num_points) {
    double circulation = 0.0;
    double d_theta = 2.0 * M_PI / num_points;

    for (int i = 0; i < num_points; ++i) {
        double theta1 = i * d_theta;
        double theta2 = (i + 1) * d_theta;

        double x1 = center_x + radius * cos(theta1);
        double y1 = center_y + radius * sin(theta1);

        double x2 = center_x + radius * cos(theta2);
        double y2 = center_y + radius * sin(theta2);

        Vector2D e1 = field(x1, y1);
        Vector2D e2 = field(x2, y2);

        /* Елементарне переміщення dl */
        double dl_x = x2 - x1;
        double dl_y = y2 - y1;

        /* Усереднене поле на кроці */
        double e_avg_x = 0.5 * (e1.x + e2.x);
        double e_avg_y = 0.5 * (e1.y + e2.y);

        /* Накопичення скалярного добутку */
        circulation += (e_avg_x * dl_x + e_avg_y * dl_y);
    }

    return circulation;
}

/* Обчислення z-компоненти ротора методом центральних різниць */
double compute_curl_z(FieldFunc field, double x, double y, double h) {
    Vector2D e_x_plus  = field(x + h, y);
    Vector2D e_x_minus = field(x - h, y);

    Vector2D e_y_plus  = field(x, y + h);
    Vector2D e_y_minus = field(x, y - h);

    double dEy_dx = (e_x_plus.y - e_x_minus.y) / (2.0 * h);
    double dEx_dy = (e_y_plus.x - e_y_minus.x) / (2.0 * h);

    return dEy_dx - dEx_dy;
}

int main(void) {
    double R = 2.5;
    int N = 1000;
    double h = 1e-5;

    printf("=== ЧИСЕЛЬНИЙ АНАЛІЗ ЦИРКУЛЯЦІЇ ТА РОТОРА (C) ===\n\n");

    /* 1. Обчислення для кулонівського поля */
    double circ_coulomb = compute_circulation(field_coulomb, 3.0, 3.0, R, N);
    double curl_coulomb = compute_curl_z(field_coulomb, 3.0, 3.0, h);

    printf("1. Кулонівське потенціальне поле:\n");
    printf("   Циркуляція по контуру (R=%.1f, N=%d):  Gamma = %.12f\n", R, N, circ_coulomb);
    printf("   Ротор у точці (3, 3) (h=%.1e):         rot_z = %.12f\n\n", h, curl_coulomb);

    /* 2. Обчислення для індукованого вихорового поля */
    double circ_vortex = compute_circulation(field_vortex, 0.0, 0.0, R, N);
    double curl_vortex = compute_curl_z(field_vortex, 1.0, 1.0, h);
    double analytical_circ = 3.0 * M_PI * R * R;

    printf("2. Індуковане вихорове поле (alpha=3.0):\n");
    printf("   Чисельна циркуляція (R=%.1f, N=%d):   Gamma = %.12f\n", R, N, circ_vortex);
    printf("   Аналітична циркуляція (alpha*pi*R^2): Gamma = %.12f\n", analytical_circ);
    printf("   Ротор у точці (1, 1) (очікується 3.0): rot_z = %.12f\n", curl_vortex);

    return 0;
}
