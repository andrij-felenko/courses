#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define MU_0 (4.0 * M_PI * 1e-7)

typedef struct {
    double x, y, z;
} Vec3;

Vec3 compute_A(Vec3 r, double R, double I, int N) {
    Vec3 a = {0.0, 0.0, 0.0};
    double dtheta = 2.0 * M_PI / (double)N;

    for (int k = 0; k < N; ++k) {
        double theta = (double)k * dtheta;
        double rx = R * cos(theta), ry = R * sin(theta);
        double dl_x = -R * sin(theta) * dtheta;
        double dl_y =  R * cos(theta) * dtheta;

        double dx = r.x - rx, dy = r.y - ry, dz = r.z;
        double dist = sqrt(dx*dx + dy*dy + dz*dz);
        if (dist > 1e-12) {
            a.x += dl_x / dist;
            a.y += dl_y / dist;
        }
    }
    double c = (MU_0 * I) / (4.0 * M_PI);
    a.x *= c; a.y *= c; a.z *= c;
    return a;
}

Vec3 compute_B_curl(Vec3 r, double R, double I, int N, double h) {
    Vec3 r_yp = {r.x, r.y+h, r.z}, r_ym = {r.x, r.y-h, r.z};
    Vec3 r_zp = {r.x, r.y, r.z+h}, r_zm = {r.x, r.y, r.z-h};
    Vec3 r_xp = {r.x+h, r.y, r.z}, r_xm = {r.x-h, r.y, r.z};

    Vec3 a_yp = compute_A(r_yp, R, I, N), a_ym = compute_A(r_ym, R, I, N);
    Vec3 a_zp = compute_A(r_zp, R, I, N), a_zm = compute_A(r_zm, R, I, N);
    Vec3 a_xp = compute_A(r_xp, R, I, N), a_xm = compute_A(r_xm, R, I, N);

    Vec3 b;
    b.x = (a_yp.z - a_ym.z)/(2*h) - (a_zp.y - a_zm.y)/(2*h);
    b.y = (a_zp.x - a_zm.x)/(2*h) - (a_xp.z - a_xm.z)/(2*h);
    b.z = (a_xp.y - a_xm.y)/(2*h) - (a_yp.x - a_ym.x)/(2*h);
    return b;
}

int main(void) {
    const double R = 0.1, I = 10.0, h = 1e-4;
    const int N = 1000;

    printf("Перевірка обчислення B = rot A на осі кільця Z:\n");
    for (double z = 0.02; z <= 0.10; z += 0.02) {
        Vec3 r = {0.0, 0.0, z};
        Vec3 b_num = compute_B_curl(r, R, I, N, h);
        double b_exact = (MU_0 * I * R * R) / (2.0 * pow(R * R + z * z, 1.5));
        printf("z = %.2f м: B_curl = %.6e Тл, B_exact = %.6e Тл (похибка %.4f%%)\n",
               z, b_num.z, b_exact, fabs(b_num.z - b_exact)/b_exact * 100.0);
    }
    return 0;
}
