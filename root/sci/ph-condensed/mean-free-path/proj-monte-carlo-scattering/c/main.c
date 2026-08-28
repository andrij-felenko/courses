#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Фундаментальні фізичні константи в одиницях СІ */
static const double CHARGE_E = 1.602176634e-19; /* Заряд електрона, Кл */
static const double MASS_E0  = 9.1093837015e-31; /* Маса спокою електрона, кг */
static const double KB_JOULE = 1.380649e-23;     /* Стала Больцмана, Дж/К */

/* Структура для представлення електрона у фазовому просторі */
typedef struct {
    double x;  /* Координата x, м */
    double vx; /* Компоненти швидкості, м/с */
    double vy;
    double vz;
} Electron;

/* Генератор рівномірного випадкового числа U ∈ (0, 1] */
static double get_random_uniform(void) {
    double u = ((double)rand() + 1.0) / ((double)RAND_MAX + 1.0);
    return (u > 1.0) ? 1.0 : u;
}

/* Визначення початкових теплових швидкостей Максвелла — Больцмана */
static void init_thermal_velocity(Electron *e, double temp_k, double m_eff) {
    double v_th = sqrt(3.0 * KB_JOULE * temp_k / m_eff);
    double cos_theta = 1.0 - 2.0 * get_random_uniform();
    double sin_theta = sqrt(fmax(0.0, 1.0 - cos_theta * cos_theta));
    double phi = 2.0 * M_PI * get_random_uniform();

    e->x  = 0.0;
    e->vx = v_th * sin_theta * cos(phi);
    e->vy = v_th * sin_theta * sin(phi);
    e->vz = v_th * cos_theta;
}

/* Головний функціонал симуляції Монте-Карло */
void run_carrier_monte_carlo(size_t num_particles, size_t num_steps,
                             double field_x, double tau_ph, double tau_imp,
                             double temp_k, double m_eff_ratio) {
    double m_eff = m_eff_ratio * MASS_E0;
    double inv_tau_ph = 1.0 / tau_ph;
    double inv_tau_imp = 1.0 / tau_imp;
    double inv_tau_tot = inv_tau_ph + inv_tau_imp;
    double tau_total = 1.0 / inv_tau_tot;
    double prob_phonon = inv_tau_ph / inv_tau_tot;

    double accel_x = -CHARGE_E * field_x / m_eff;

    Electron *ensemble = (Electron*)malloc(num_particles * sizeof(Electron));
    if (!ensemble) {
        fprintf(stderr, "Помилка виділення пам'яті під ансамбль носіїв.\n");
        return;
    }

    /* Ініціалізація носіїв з урахуванням теплового руху */
    for (size_t i = 0; i < num_particles; ++i) {
        init_thermal_velocity(&ensemble[i], temp_k, m_eff);
    }

    double grand_total_path = 0.0;
    double grand_total_time = 0.0;
    size_t grand_total_events = 0;
    size_t phonon_events = 0;
    size_t impurity_events = 0;

    /* Основний цикл моделювання */
    for (size_t step = 0; step < num_steps; ++step) {
        for (size_t i = 0; i < num_particles; ++i) {
            /* 1. Генерація тривалості вільного польоту */
            double u = get_random_uniform();
            double dt = -tau_total * log(u);

            /* 2. Прискорення полем між зіткненнями */
            double vx_old = ensemble[i].vx;
            ensemble[i].vx += accel_x * dt;
            double vx_avg = 0.5 * (vx_old + ensemble[i].vx);
            ensemble[i].x += vx_avg * dt;

            /* Розрахунок модуля швидкості та пройденого шляху */
            double v_mag = sqrt(ensemble[i].vx * ensemble[i].vx +
                                ensemble[i].vy * ensemble[i].vy +
                                ensemble[i].vz * ensemble[i].vz);

            grand_total_path += v_mag * dt;
            grand_total_time += dt;
            grand_total_events++;

            /* 3. Вибір механізму розсіювання */
            double u_mech = get_random_uniform();
            if (u_mech <= prob_phonon) {
                phonon_events++;
            } else {
                impurity_events++;
            }

            /* 4. Ізотропне перевизначення кутів швидкості */
            double cos_th = 1.0 - 2.0 * get_random_uniform();
            double sin_th = sqrt(fmax(0.0, 1.0 - cos_th * cos_th));
            double phi_angle = 2.0 * M_PI * get_random_uniform();

            ensemble[i].vx = v_mag * sin_th * cos(phi_angle);
            ensemble[i].vy = v_mag * sin_th * sin(phi_angle);
            ensemble[i].vz = v_mag * cos_th;
        }
    }

    /* Розрахунок підсумкової статистики */
    double mean_tau = grand_total_time / (double)grand_total_events;
    double mean_lambda_nm = (grand_total_path / (double)grand_total_events) * 1e9;

    double sum_vx = 0.0;
    double sum_energy_ev = 0.0;
    for (size_t i = 0; i < num_particles; ++i) {
        sum_vx += ensemble[i].vx;
        double v_sq = ensemble[i].vx * ensemble[i].vx +
                      ensemble[i].vy * ensemble[i].vy +
                      ensemble[i].vz * ensemble[i].vz;
        double energy_j = 0.5 * m_eff * v_sq;
        sum_energy_ev += energy_j / CHARGE_E;
    }
    double drift_velocity = sum_vx / (double)num_particles;
    double mean_energy_ev = sum_energy_ev / (double)num_particles;

    printf("====================================================\n");
    printf("     РЕЗУЛЬТАТИ СИМУЛЯЦІЇ МОНТЕ-КАРЛО (мова C)\n");
    printf("====================================================\n");
    printf("Кількість носіїв:                  %zu\n", num_particles);
    printf("Загальна кількість зіткнень:       %zu\n", grand_total_events);
    printf("Актів фононного розсіювання:       %zu (%.1f%%)\n", 
           phonon_events, 100.0 * (double)phonon_events / grand_total_events);
    printf("Актів домішкового розсіювання:     %zu (%.1f%%)\n", 
           impurity_events, 100.0 * (double)impurity_events / grand_total_events);
    printf("----------------------------------------------------\n");
    printf("Розрахований час релаксації tau:    %.3e с (теорія: %.3e с)\n", 
           mean_tau, tau_total);
    printf("Довжина вільного пробігу lambda:   %.2f нм\n", mean_lambda_nm);
    printf("Середня дрейфова швидкість v_d:     %.3e м/с\n", drift_velocity);
    printf("Середня кінетична енергія <E>:     %.3f еВ\n", mean_energy_ev);
    printf("====================================================\n");

    free(ensemble);
}

int main(void) {
    srand(42); /* Фіксоване зерно генератора випадкових чисел */

    /* Параметри моделювання для Si: E = 10^5 В/м, T = 300 K, m* = 0.26 m_0 */
    run_carrier_monte_carlo(2000, 400, 1e5, 120e-15, 240e-15, 300.0, 0.26);

    return 0;
}
