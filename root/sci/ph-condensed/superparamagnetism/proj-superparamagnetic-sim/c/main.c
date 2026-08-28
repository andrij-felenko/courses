#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double x, y, z;
} Vec3;

static Vec3 vec3_cross(Vec3 a, Vec3 b) {
    Vec3 r = {
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
    return r;
}

static Vec3 vec3_normalize(Vec3 v) {
    double len = sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
    if (len < 1e-15) len = 1.0;
    Vec3 r = { v.x / len, v.y / len, v.z / len };
    return r;
}

/* Генератор випадкових чисел Box-Muller для нормально розподілених величин N(0,1) */
static double rand_gaussian(void) {
    double u1 = ((double)rand() + 1.0) / ((double)RAND_MAX + 1.0);
    double u2 = ((double)rand() + 1.0) / ((double)RAND_MAX + 1.0);
    return sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2);
}

/* Розрахунок похідної dm/dt за рівнянням sLLG */
static Vec3 sllg_rhs(Vec3 m, Vec3 h_eff, double gamma_prime, double alpha) {
    Vec3 m_cross_h = vec3_cross(m, h_eff);
    Vec3 m_cross_m_cross_h = vec3_cross(m, m_cross_h);
    
    Vec3 dmdt = {
        -gamma_prime * m_cross_h.x - alpha * gamma_prime * m_cross_m_cross_h.x,
        -gamma_prime * m_cross_h.y - alpha * gamma_prime * m_cross_m_cross_h.y,
        -gamma_prime * m_cross_h.z - alpha * gamma_prime * m_cross_m_cross_h.z
    };
    return dmdt;
}

int main(void) {
    srand((unsigned int)time(NULL));

    /* Фізичні константи */
    const double kB = 1.380649e-23;    /* Дж/К */
    const double gamma = 1.76e11;       /* rad/(s*T) */

    /* Параметри матеріалу (Co наночастинка) */
    const double Ms = 1.4e6;            /* А/м */
    const double Ku = 4.5e5;            /* Дж/м3 */
    const double diameter = 8.0e-9;      /* 8 нм */
    const double V = (M_PI / 6.0) * diameter * diameter * diameter;
    const double alpha = 0.1;
    const double T = 300.0;             /* Кімнатна температура К */

    const double gamma_prime = gamma / (1.0 + alpha * alpha);
    const double Hk = 2.0 * Ku / Ms;    /* Поле анізотропії, Тл */
    const double stdev_h_th = sqrt((2.0 * alpha * kB * T) / (gamma * Ms * V));

    /* Параметри чисельного інтегрування */
    const double dt = 1.0e-13;          /* Крок за часом 0.1 пс */
    const long num_steps = 5000000;    /* 0.5 мкс сумуляції */

    Vec3 m = { 0.0, 0.0, 1.0 };         /* Старт з верхнього мінімуму +M_z */

    long flip_count = 0;
    int current_state = 1;              /* 1 для m_z > 0, -1 для m_z < 0 */

    printf("=== Симуляція термофлуктуацій макроспіна (C) ===\n");
    printf("Діаметр частини: %.1f нм, Температура: %.0f K\n", diameter * 1e9, T);
    printf("Енергетичний бар'єр Ku*V / kB*T: %.2f\n", (Ku * V) / (kB * T));
    printf("Поле анізотропії Hk: %.3f Tл\n\n", Hk);

    for (long step = 0; step < num_steps; step++) {
        /* Згенелювати випадкове поле Ланжевена для даного кроку */
        double dt_sqrt = sqrt(dt);
        Vec3 h_th = {
            stdev_h_th * rand_gaussian() / dt_sqrt,
            stdev_h_th * rand_gaussian() / dt_sqrt,
            stdev_h_th * rand_gaussian() / dt_sqrt
        };

        /* Ефективне поле: анізотропія + шум */
        Vec3 h_eff = { h_th.x, h_th.y, Hk * m.z + h_th.z };

        /* Метод Хена (Предиктор) */
        Vec3 k1 = sllg_rhs(m, h_eff, gamma_prime, alpha);
        Vec3 m_pred = {
            m.x + k1.x * dt,
            m.y + k1.y * dt,
            m.z + k1.z * dt
        };
        m_pred = vec3_normalize(m_pred);

        /* Коректор */
        Vec3 h_eff_pred = { h_th.x, h_th.y, Hk * m_pred.z + h_th.z };
        Vec3 k2 = sllg_rhs(m_pred, h_eff_pred, gamma_prime, alpha);

        m.x += 0.5 * (k1.x + k2.x) * dt;
        m.y += 0.5 * (k1.y + k2.y) * dt;
        m.z += 0.5 * (k1.z + k2.z) * dt;
        m = vec3_normalize(m);

        /* Фіксація перевертань */
        if (current_state == 1 && m.z < -0.2) {
            current_state = -1;
            flip_count++;
        } else if (current_state == -1 && m.z > 0.2) {
            current_state = 1;
            flip_count++;
        }
    }

    double sim_time = num_steps * dt;
    double tau_theoretical = 1e-9 * exp((Ku * V) / (kB * T));

    printf("Час моделювання: %.2e с\n", sim_time);
    printf("Кількість перевертань макроспіна: %ld\n", flip_count);
    printf("Теоретичний час Нееля-Брауна: %.2e с\n", tau_theoretical);

    return 0;
}
