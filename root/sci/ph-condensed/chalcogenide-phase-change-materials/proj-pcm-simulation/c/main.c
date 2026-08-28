#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define M_PI 3.14159265358979323846

/* Фізичні константи та параметри матеріалу GST-225 */
typedef struct {
    double length;            /* товщина шару (м) */
    double temp_bg;           /* фонова температура (К) */
    double temp_melt;         /* температура плавлення (К) */
    double temp_glass;        /* температура склування (К) */
    double cp_base;           /* об'ємна теплоємність (Дж/(м³·К)) */
    double latent_heat;       /* прихована теплота плавлення (Дж/кг) */
    double density;           /* густина речовини (кг/м³) */
    double kappa_amo;         /* теплопровідність аморфної фази (Вт/(м·К)) */
    double kappa_cry;         /* теплопровідність кристалічної фази (Вт/(м·К)) */
    double rho_amo;           /* питомий опір аморфного стану (Ом·м) */
    double rho_cry;           /* питомий опір кристалічного стану (Ом·м) */
    double avrami_n;          /* показник Аврамі n */
    double jmak_k0;           /* предекспонента K0 (1/c^n) */
    double activation_energy; /* енергія активації (Дж) */
} PcmParams;

/* Стан просторової сітки */
typedef struct {
    int num_nodes;
    double dx;
    double *temp;
    double *cryst_fraction;
} PcmGrid;

/* Ініціалізація просторової сітки */
bool pcm_grid_init(PcmGrid *grid, int num_nodes, double length, double initial_temp, double initial_cryst) {
    grid->num_nodes = num_nodes;
    grid->dx = length / (num_nodes - 1);
    grid->temp = (double *)malloc(num_nodes * sizeof(double));
    grid->cryst_fraction = (double *)malloc(num_nodes * sizeof(double));
    if (!grid->temp || !grid->cryst_fraction) {
        free(grid->temp);
        free(grid->cryst_fraction);
        return false;
    }
    for (int i = 0; i < num_nodes; ++i) {
        grid->temp[i] = initial_temp;
        grid->cryst_fraction[i] = initial_cryst;
    }
    return true;
}

void pcm_grid_free(PcmGrid *grid) {
    free(grid->temp);
    free(grid->cryst_fraction);
    grid->temp = NULL;
    grid->cryst_fraction = NULL;
}

/* Ефективна теплоємність із урахуванням прихованої теплоти плавлення */
static double get_effective_cp(double temp, const PcmParams *p) {
    double dt_melt = 5.0; /* напівширина розмиття плавлення */
    if (fabs(temp - p->temp_melt) <= dt_melt) {
        double cp_latent = (p->density * p->latent_heat) / (2.0 * dt_melt);
        return p->cp_base + cp_latent;
    }
    return p->cp_base;
}

/* Обчислення кінетичної константи JMAK K(T) */
static double calc_jmak_k(double temp, const PcmParams *p) {
    if (temp < p->temp_glass || temp >= p->temp_melt) {
        return 0.0;
    }
    const double kb = 1.380649e-23;
    double dt_norm = (temp - p->temp_glass) / (p->temp_melt - p->temp_glass);
    double shape = 4.0 * dt_norm * (1.0 - dt_norm);
    return p->jmak_k0 * exp(-p->activation_energy / (kb * temp)) * shape;
}

/* Крок часової інтеграції термо-кінетичних рівнянь */
void pcm_simulate_step(PcmGrid *grid, const PcmParams *params, double current_density, double dt) {
    int n = grid->num_nodes;
    double dx = grid->dx;
    double *next_temp = (double *)malloc(n * sizeof(double));
    if (!next_temp) return;

    /* 1. Оновлення кінетики кристалізації X(t) та плавлення */
    for (int i = 0; i < n; ++i) {
        double t_curr = grid->temp[i];
        if (t_curr >= params->temp_melt) {
            /* Миттєве плавлення при перевищенні T_m */
            grid->cryst_fraction[i] = 0.0;
        } else {
            double x_curr = grid->cryst_fraction[i];
            if (x_curr < 0.999) {
                double k_val = calc_jmak_k(t_curr, params);
                if (k_val > 0.0) {
                    double n_av = params->avrami_n;
                    double one_minus_x = 1.0 - x_curr;
                    if (one_minus_x < 1e-6) one_minus_x = 1e-6;
                    double ln_term = -log(one_minus_x);
                    if (ln_term < 1e-6) ln_term = 1e-6;
                    double dx_dt = n_av * pow(k_val, 1.0 / n_av) * one_minus_x * pow(ln_term, (n_av - 1.0) / n_av);
                    grid->cryst_fraction[i] += dx_dt * dt;
                    if (grid->cryst_fraction[i] > 1.0) grid->cryst_fraction[i] = 1.0;
                }
            }
        }
    }

    /* 2. Теплопровідність та Джоулів розігрів */
    next_temp[0] = params->temp_bg;         /* Гранична умова Діріхле на лівому контакті */
    next_temp[n - 1] = params->temp_bg;     /* Гранична умова Діріхле на правому контакті */

    for (int i = 1; i < n - 1; ++i) {
        double x_frac = grid->cryst_fraction[i];
        double kappa = x_frac * params->kappa_cry + (1.0 - x_frac) * params->kappa_amo;
        double rho = x_frac * params->rho_cry + (1.0 - x_frac) * params->rho_amo;
        double cp_eff = get_effective_cp(grid->temp[i], params);

        double d2t_dx2 = (grid->temp[i + 1] - 2.0 * grid->temp[i] + grid->temp[i - 1]) / (dx * dx);
        double joule_heat = current_density * current_density * rho;

        next_temp[i] = grid->temp[i] + (dt / cp_eff) * (kappa * d2t_dx2 + joule_heat);
    }

    for (int i = 0; i < n; ++i) {
        grid->temp[i] = next_temp[i];
    }
    free(next_temp);
}

int main(void) {
    PcmParams p = {
        .length = 50e-9,
        .temp_bg = 300.0,
        .temp_melt = 873.0,
        .temp_glass = 473.0,
        .cp_base = 1.25e6,
        .latent_heat = 1.3e5,
        .density = 6150.0,
        .kappa_amo = 0.2,
        .kappa_cry = 0.5,
        .rho_amo = 1.0e-2,
        .rho_cry = 1.0e-5,
        .avrami_n = 3.0,
        .jmak_k0 = 1.0e11,
        .activation_energy = 2.4e-19
    };

    PcmGrid grid;
    if (!pcm_grid_init(&grid, 51, p.length, 300.0, 1.0)) {
        printf("Помилка виділення пам'яті сітки\n");
        return 1;
    }

    printf("--- Моделювання RESET імпульсу (Аморфізація) ---\n");
    double j_reset = 1.5e11; /* 1.5e11 А/м² */
    double dt = 1e-13;       /* 0.1 пс часовий крок */

    for (int step = 0; step < 50000; ++step) {
        pcm_simulate_step(&grid, &p, j_reset, dt);
    }

    printf("Максимальна температура в центрі: %.1f K\n", grid.temp[25]);
    printf("Кристалічна частка в центрі: %.3f\n", grid.cryst_fraction[25]);

    pcm_grid_free(&grid);
    return 0;
}
