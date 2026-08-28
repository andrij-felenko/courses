#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Фізичні константи */
#define KB_EV 8.617333262145e-5      /* Стала Больцмана в еВ/К */
#define HBAR_EV_S 6.582119569e-16    /* Зведена стала Планка в еВ·с */
#define ME_KG 9.1093837015e-31       /* Маса спокою електрона в кг */

typedef struct {
    double temp_k;        /* Температура в Кельвінах */
    double n_d;           /* Концентрація донорів в см⁻³ */
    double e_d_relative;  /* Енергія донора відносно Ec (еВ, наприклад 0.045) */
    double n_a;           /* Концентрація акцепторів в см⁻³ */
    double e_a_relative;  /* Енергія акцептора відносно Ev (еВ, наприклад 0.045) */
    double m_e_eff;       /* Ефективна маса електрона (в одиницях m0) */
    double m_h_eff;       /* Ефективна маса дірки (в одиницях m0) */
} silicon_config_t;

typedef struct {
    double e_v;
    double e_c;
    double e_g;
    double e_f;
    double n_elec;
    double p_hole;
    double n_d_plus;
    double n_a_minus;
} solver_result_t;

/* Обчислення ширини забороненої зони Si за формулою Варшні */
static double calculate_bandgap_varshni(double temp_k) {
    double eg0 = 1.166; /* еВ */
    double alpha = 4.73e-4;
    double beta = 636.0;
    return eg0 - (alpha * temp_k * temp_k) / (temp_k + beta);
}

/* Обчислення ефективної густини станів Nc та Nv */
static void calculate_effective_dos(double temp_k, double me_eff, double mh_eff, double *nc, double *nv) {
    double t_factor = temp_k / 300.0;
    *nc = 2.86e19 * pow(me_eff / 1.08, 1.5) * pow(t_factor, 1.5);
    *nv = 3.10e19 * pow(mh_eff / 0.81, 1.5) * pow(t_factor, 1.5);
}

/* Функція некомпенсованого заряду: f(Ef) = p + Nd+ - n - Na- */
static double charge_residual(double e_f, double e_c, double e_v, double e_d, double e_a, 
                               double nc, double nv, const silicon_config_t *cfg) {
    double kt = KB_EV * cfg->temp_k;

    /* Обмеження аргументу експоненти для запобігання overflow */
    double arg_n = -(e_c - e_f) / kt;
    double arg_p = -(e_f - e_v) / kt;
    if (arg_n > 80.0) arg_n = 80.0;
    if (arg_p > 80.0) arg_p = 80.0;

    double n = nc * exp(arg_n);
    double p = nv * exp(arg_p);

    /* Іонізовані домішки */
    double arg_d = (e_f - e_d) / kt;
    double arg_a = (e_a - e_f) / kt;
    if (arg_d > 80.0) arg_d = 80.0;
    if (arg_a > 80.0) arg_a = 80.0;

    double n_d_plus = cfg->n_d / (1.0 + 2.0 * exp(arg_d));
    double n_a_minus = cfg->n_a / (1.0 + 4.0 * exp(arg_a));

    return (p + n_d_plus) - (n + n_a_minus);
}

/* Чисельний солвер методом бісекції */
int solve_fermi_level_c(const silicon_config_t *cfg, solver_result_t *res) {
    if (cfg->temp_k <= 0.0) return -1;

    res->e_v = 0.0;
    res->e_g = calculate_bandgap_varshni(cfg->temp_k);
    res->e_c = res->e_v + res->e_g;

    double e_d = res->e_c - cfg->e_d_relative;
    double e_a = res->e_v + cfg->e_a_relative;

    double nc = 0.0, nv = 0.0;
    calculate_effective_dos(cfg->temp_k, cfg->m_e_eff, cfg->m_h_eff, &nc, &nv);

    double e_low = res->e_v - 0.5;
    double e_high = res->e_c + 0.5;
    double e_mid = (e_low + e_high) / 2.0;

    /* Метод бісекції (60 ітерацій забезпечують граничну точність типу double) */
    for (int iter = 0; iter < 60; iter++) {
        e_mid = (e_low + e_high) / 2.0;
        double f_mid = charge_residual(e_mid, res->e_c, res->e_v, e_d, e_a, nc, nv, cfg);

        if (f_mid > 0.0) {
            e_low = e_mid;
        } else {
            e_high = e_mid;
        }
    }

    res->e_f = e_mid;
    double kt = KB_EV * cfg->temp_k;

    res->n_elec = nc * exp(-(res->e_c - res->e_f) / kt);
    res->p_hole = nv * exp(-(res->e_f - res->e_v) / kt);
    res->n_d_plus = cfg->n_d / (1.0 + 2.0 * exp((res->e_f - e_d) / kt));
    res->n_a_minus = cfg->n_a / (1.0 + 4.0 * exp((e_a - res->e_f) / kt));

    return 0;
}

int main(void) {
    silicon_config_t cfg_n = {
        .temp_k = 300.0,
        .n_d = 1.0e16,
        .e_d_relative = 0.045,
        .n_a = 0.0,
        .e_a_relative = 0.045,
        .m_e_eff = 1.08,
        .m_h_eff = 0.81
    };

    solver_result_t res;
    if (solve_fermi_level_c(&cfg_n, &res) == 0) {
        printf("--- Розрахунок Si n-типу (T = %.1f K, Nd = %.1e cm^-3) ---\n", cfg_n.temp_k, cfg_n.n_d);
        printf("Ширина забороненої зони Eg = %.4f еВ\n", res.e_g);
        printf("Рівень Фермі Ef = %.4f еВ (відносно Ev)\n", res.e_f);
        printf("Відстань Ec - Ef = %.4f еВ\n", res.e_c - res.e_f);
        printf("Концентрація електронів n = %.3e см^-3\n", res.n_elec);
        printf("Частка іонізованих донорів Nd+/Nd = %.1f%%\n", (res.n_d_plus / cfg_n.n_d) * 100.0);
    }

    return 0;
}
