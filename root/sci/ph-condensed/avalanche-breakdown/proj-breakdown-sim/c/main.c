#include <stdio.h>
#include <math.h>

#define K_BOLTZMANN 8.61733e-5 /* еВ/К */
#define EG_SILICON  1.12       /* еВ */

typedef struct {
    double v_br0;    /* Напруга пробою при 25 °C (В) */
    double tc_v;     /* Температурний коефіцієнт (1/°C) */
    double i_s0;     /* Зворотний струм витоку при 25 °C (А) */
    double n_miller; /* Показник степеня Міллера */
    double r_series; /* Внутрішній опір кристала (Ом) */
} DiodeParams;

/* Розрахунок зворотного струму діода I_R при заданій напрузі V_d та температурі temp_c */
double calculate_reverse_current(double v_d, double temp_c, const DiodeParams *p) {
    if (v_d <= 0.0) return 0.0;

    double t_kelvin = temp_c + 273.15;
    double t0_kelvin = 298.15;

    /* Температурна залежність струму витоку */
    double i_s = p->i_s0 * pow(t_kelvin / t0_kelvin, 3.0) *
                 exp(-(EG_SILICON / (2.0 * K_BOLTZMANN * t_kelvin)) * (1.0 - t_kelvin / t0_kelvin));

    /* Напруга пробою з урахуванням температури */
    double v_br = p->v_br0 * (1.0 + p->tc_v * (temp_c - 25.0));

    if (v_d >= v_br) {
        /* В області глибокого пробою струм обмежується опіром кристала */
        double v_over = v_d - v_br;
        return (i_s * 1000.0) + (v_over / p->r_series);
    }

    /* Коефіцієнт множення Міллера в передпробійній області */
    double ratio = v_d / v_br;
    double m_factor = 1.0 / (1.0 - pow(ratio, p->n_miller));
    if (m_factor > 1e4) m_factor = 1e4;

    return i_s * m_factor;
}

/* Знаходження робочої точки кола методом ділення навпіл (метод бісекції) */
double solve_operating_point(double v_src, double r_ballast, double temp_c, const DiodeParams *p) {
    double v_low = 0.0;
    double v_high = v_src;
    double v_mid = 0.0;

    for (int iter = 0; iter < 50; iter++) {
        v_mid = 0.5 * (v_low + v_high);
        double i_d = calculate_reverse_current(v_mid, temp_c, p);
        double v_drop = v_src - i_d * r_ballast;

        if (v_drop > v_mid) {
            v_low = v_mid;
        } else {
            v_high = v_mid;
        }
    }
    return v_mid;
}

int main(void) {
    /* 1N4734A: Зенерівський діод 5.6 В (ТКН близько 0) */
    DiodeParams zener5v6 = {
        .v_br0 = 5.6,
        .tc_v = 0.0001,
        .i_s0 = 1e-7,
        .n_miller = 4.0,
        .r_series = 2.0
    };

    /* 1N4742A: Лавинний стабілітрон 12 В (додатний ТКН) */
    DiodeParams zener12v = {
        .v_br0 = 12.0,
        .tc_v = 0.00085,
        .i_s0 = 1e-8,
        .n_miller = 5.0,
        .r_series = 4.5
    };

    printf("=== Симуляція робочої точки кола стабілізації ===\n");
    double v_supply = 18.0;   /* Напруга живлення 18 В */
    double r_ext = 470.0;     /* Баластний резистор 470 Ом */

    for (double temp = 0.0; temp <= 100.0; temp += 25.0) {
        double v_d5 = solve_operating_point(v_supply, r_ext, temp, &zener5v6);
        double i_d5 = calculate_reverse_current(v_d5, temp, &zener5v6);

        double v_d12 = solve_operating_point(v_supply, r_ext, temp, &zener12v);
        double i_d12 = calculate_reverse_current(v_d12, temp, &zener12v);

        printf("T = %3.0f °C | 5.6V Diod: V = %.3f В, I = %6.2f мА | 12V Diod: V = %.3f В, I = %6.2f мА\n",
               temp, v_d5, i_d5 * 1000.0, v_d12, i_d12 * 1000.0);
    }

    return 0;
}
