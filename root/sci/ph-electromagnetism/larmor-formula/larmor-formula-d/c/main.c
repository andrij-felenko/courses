#include <stdio.h>
#include <math.h>

/* Фізичні константи */
#define C_LIGHT 2.99792458e8
#define EPS0    8.8541878128e-12
#define Q_ELEM  1.602176634e-19
#define M_ELEM  9.1093837015e-31
#define PI_VAL  3.141592653589793

/* Миттєва потужність Лармора за 3D-вектором прискорення */
double larmor_power(double ax, double ay, double az) {
    double a_sq = ax * ax + ay * ay + az * az;
    return (Q_ELEM * Q_ELEM * a_sq) / (6.0 * PI_VAL * EPS0 * C_LIGHT * C_LIGHT * C_LIGHT);
}

int main(void) {
    /* Моделювання електрона, що коливається в полі світлової хвилі E = E0 * sin(omega * t) */
    const double E0 = 1.0e6;                  /* Амплітуда поля, В/м */
    const double FREQ = 5.0e14;               /* Оптична частота, Гц */
    const double OMEGA = 2.0 * PI_VAL * FREQ;
    const double DT = 1.0e-17;                /* Крок часу, с */
    const int STEPS = 1000;

    double t = 0.0;
    double total_energy = 0.0;

    printf("Час (фс) | Поле (кВ/м) | Прискорення (10^17 м/с^2) | Потужність (пВт)\n");
    printf("--------------------------------------------------------------------\n");

    for (int i = 0; i <= STEPS; ++i) {
        double E_field = E0 * sin(OMEGA * t);
        double a_x = (-Q_ELEM * E_field) / M_ELEM;
        double P_rad = larmor_power(a_x, 0.0, 0.0);

        total_energy += P_rad * DT;

        if (i % 200 == 0) {
            printf("%8.3f | %11.2f | %26.4f | %16.4e\n",
                   t * 1.0e15, E_field * 1.0e-3, a_x * 1.0e-17, P_rad * 1.0e12);
        }
        t += DT;
    }

    printf("\nПовна випромінена енергія за період: %.6e Дж\n", total_energy);
    return 0;
}
