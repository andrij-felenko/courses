#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define MU_0 (4.0 * M_PI * 1e-7)

typedef struct {
    double x;
    double y;
    double z;
} Vec3;

static inline Vec3 vec3_add(Vec3 a, Vec3 b) {
    Vec3 r = {a.x + b.x, a.y + b.y, a.z + b.z};
    return r;
}

static inline Vec3 vec3_scale(Vec3 a, double s) {
    Vec3 r = {a.x * s, a.y * s, a.z * s};
    return r;
}

/* Обчислення векторного потенціалу A кругового витка у точці r */
Vec3 compute_vector_potential(Vec3 r, double radius, double current, int segments) {
    Vec3 a = {0.0, 0.0, 0.0};
    double d_theta = 2.0 * M_PI / (double)segments;

    for (int k = 0; k < segments; ++k) {
        double theta = (double)k * d_theta;
        double rk_x = radius * cos(theta);
        double rk_y = radius * sin(theta);
        double rk_z = 0.0;

        double dl_x = -radius * sin(theta) * d_theta;
        double dl_y =  radius * cos(theta) * d_theta;
        double dl_z =  0.0;

        double dx = r.x - rk_x;
        double dy = r.y - rk_y;
        double dz = r.z - rk_z;
        double dist = sqrt(dx * dx + dy * dy + dz * dz);

        if (dist > 1e-12) {
            a.x += dl_x / dist;
            a.y += dl_y / dist;
            a.z += dl_z / dist;
        }
    }

    double factor = (MU_0 * current) / (4.0 * M_PI);
    return vec3_scale(a, factor);
}

/* Обчислення магнітної індукції B = rot A через центральні скінченні різниці */
Vec3 compute_magnetic_field_curl(Vec3 r, double radius, double current, int segments, double h) {
    Vec3 r_yp = {r.x, r.y + h, r.z};
    Vec3 r_ym = {r.x, r.y - h, r.z};
    Vec3 r_zp = {r.x, r.y, r.z + h};
    Vec3 r_zm = {r.x, r.y, r.z - h};
    Vec3 r_xp = {r.x + h, r.y, r.z};
    Vec3 r_xm = {r.x - h, r.y, r.z};

    Vec3 a_yp = compute_vector_potential(r_yp, radius, current, segments);
    Vec3 a_ym = compute_vector_potential(r_ym, radius, current, segments);
    Vec3 a_zp = compute_vector_potential(r_zp, radius, current, segments);
    Vec3 a_zm = compute_vector_potential(r_zm, radius, current, segments);
    Vec3 a_xp = compute_vector_potential(r_xp, radius, current, segments);
    Vec3 a_xm = compute_vector_potential(r_xm, radius, current, segments);

    double dAz_dy = (a_yp.z - a_ym.z) / (2.0 * h);
    double dAy_dz = (a_zp.y - a_zm.y) / (2.0 * h);

    double dAx_dz = (a_zp.x - a_zm.x) / (2.0 * h);
    double dAz_dx = (a_xp.z - a_xp.z) / (2.0 * h);

    double dAy_dx = (a_xp.y - a_xm.y) / (2.0 * h);
    double dAx_dy = (a_yp.x - a_ym.x) / (2.0 * h);

    Vec3 b;
    b.x = dAz_dy - dAy_dz;
    b.y = dAx_dz - dAz_dx;
    b.z = dAy_dx - dAx_dy;
    return b;
}

int main(void) {
    const double radius = 0.1;       /* Радіус витка R = 0.1 м */
    const double current = 10.0;     /* Струм I = 10 А */
    const int segments = 1000;       /* Кількість сегментів дискретизації */
    const double h = 1e-4;           /* Крок чисельного диференціювання */

    printf("Порівняння чисельного B = rot A з аналітичною формулою на осі Z:\n");
    printf("%8s | %14s | %14s | %12s\n", "z, м", "B_num (T)", "B_exact (T)", "Похибка (%)");
    printf("-----------------------------------------------------------------\n");

    for (double z = 0.02; z <= 0.20; z += 0.02) {
        Vec3 r = {0.0, 0.0, z};
        Vec3 b_num = compute_magnetic_field_curl(r, radius, current, segments, h);

        double b_exact = (MU_0 * current * radius * radius) /
                         (2.0 * pow(radius * radius + z * z, 1.5));
        double err = fabs(b_num.z - b_exact) / b_exact * 100.0;

        printf("%8.2f | %14.6e | %14.6e | %11.4f%%\n", z, b_num.z, b_exact, err);
    }

    return 0;
}
