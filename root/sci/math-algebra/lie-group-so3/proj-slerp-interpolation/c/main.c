#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double w, x, y, z;
} Quat;

Quat quat_normalize(Quat q) {
    double mag = sqrt(q.w * q.w + q.x * q.x + q.y * q.y + q.z * q.z);
    if (mag < 1e-12) {
        Quat id = {1.0, 0.0, 0.0, 0.0};
        return id;
    }
    Quat res = {q.w / mag, q.x / mag, q.y / mag, q.z / mag};
    return res;
}

double quat_dot(Quat a, Quat b) {
    return a.w * b.w + a.x * b.x + a.y * b.y + a.z * b.z;
}

Quat quat_slerp(Quat q1, Quat q2, double t) {
    double dot = quat_dot(q1, q2);

    /* Вибір найкоротшого шляху на 3-сфері S3 */
    if (dot < 0.0) {
        dot = -dot;
        q2.w = -q2.w;
        q2.x = -q2.x;
        q2.y = -q2.y;
        q2.z = -q2.z;
    }

    /* Захист від похибок переповнення acos() через машинне округлення */
    if (dot > 1.0) {
        dot = 1.0;
    }

    /* Якщо кут майже нульовий, використовуємо стійку NLERP */
    if (dot > 0.9995) {
        Quat result = {
            q1.w + t * (q2.w - q1.w),
            q1.x + t * (q2.x - q1.x),
            q1.y + t * (q2.y - q1.y),
            q1.z + t * (q2.z - q1.z)
        };
        return quat_normalize(result);
    }

    /* Класична формула SLERP */
    double omega = acos(dot);
    double sin_omega = sin(omega);
    double scale1 = sin((1.0 - t) * omega) / sin_omega;
    double scale2 = sin(t * omega) / sin_omega;

    Quat result = {
        scale1 * q1.w + scale2 * q2.w,
        scale1 * q1.x + scale2 * q2.x,
        scale1 * q1.y + scale2 * q2.y,
        scale1 * q1.z + scale2 * q2.z
    };
    return result;
}

int main(void) {
    /* Початкова орієнтація: без повороту (I) */
    Quat q1 = {1.0, 0.0, 0.0, 0.0};
    /* Кінцева орієнтація: поворот на 90° навколо осі Z */
    Quat q2 = {cos(M_PI / 4.0), 0.0, 0.0, sin(M_PI / 4.0)};

    printf("Кроки інтерполяції SLERP (C):\n");
    for (int i = 0; i <= 4; ++i) {
        double t = i * 0.25;
        Quat qt = quat_slerp(q1, q2, t);
        printf("t = %.2f -> (w: %.4f, x: %.4f, y: %.4f, z: %.4f)\n",
               t, qt.w, qt.x, qt.y, qt.z);
    }
    return 0;
}
