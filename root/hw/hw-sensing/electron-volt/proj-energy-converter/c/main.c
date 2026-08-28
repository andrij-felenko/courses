#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Константи системи SI та фізичні параметри */
#define C_SPEED 299792458.0
#define E_CHARGE 1.602176634e-19
#define KB_JOULE 1.380649e-23
#define HC_EV_NM 1239.84198

#define MASS_ELECTRON_EV 510998.95
#define MASS_PROTON_EV   938272088.16
#define MASS_ALPHA_EV    3727379400.0

typedef struct {
    double total_kin_ev;
    double gamma;
    double beta;
    double velocity_m_s;
    double momentum_ev_c;
    double de_broglie_nm;
    double temp_kelvin;
} particle_kinematics_t;

/**
 * Обчислює кінетичні параметри частинки.
 * 
 * @param energy_ev Прискорювальна напруга в вольтах (або енергія eV).
 * @param rest_mass_ev Маса спокою у еВ (m c^2).
 * @param charge_z Кратність заряду (z >= 1).
 * @param out Вказівник на структуру для запису результатів.
 * @return true у разі успішного розрахунку, false при некоректних вхідних даних.
 */
bool compute_particle_kinematics(double energy_ev, double rest_mass_ev, int charge_z, particle_kinematics_t *out) {
    if (energy_ev < 0.0 || rest_mass_ev <= 0.0 || charge_z <= 0 || out == NULL) {
        return false;
    }

    out->total_kin_ev = energy_ev * (double)charge_z;
    double eps = out->total_kin_ev / rest_mass_ev;
    out->gamma = 1.0 + eps;

    /* Вибір чисельно стабільного алгоритму для β */
    if (eps < 1e-5) {
        out->beta = sqrt(2.0 * eps) * (1.0 - 0.375 * eps + 0.3125 * eps * eps);
    } else {
        out->beta = sqrt(1.0 - 1.0 / (out->gamma * out->gamma));
    }

    out->velocity_m_s = out->beta * C_SPEED;
    out->momentum_ev_c = sqrt(out->total_kin_ev * (out->total_kin_ev + 2.0 * rest_mass_ev));
    out->de_broglie_nm = (out->momentum_ev_c > 0.0) ? (HC_EV_NM / out->momentum_ev_c) : 0.0;

    double energy_joules = out->total_kin_ev * E_CHARGE;
    out->temp_kelvin = energy_joules / KB_JOULE;

    return true;
}

int main(void) {
    particle_kinematics_t kin;

    printf("=== Симуляція кінетики (C implementation) ===\n");
    if (compute_particle_kinematics(510998.95, MASS_ELECTRON_EV, 1, &kin)) {
        printf("Релятивістський електрон (E_k = m_e c^2):\n");
        printf("  Загальна енергія: %.2f кеВ\n", kin.total_kin_ev / 1000.0);
        printf("  Фактор Лоренца γ: %.4f\n", kin.gamma);
        printf("  Швидкість v/c: %.5f (v = %.4e м/с)\n", kin.beta, kin.velocity_m_s);
        printf("  Імпульс p*c: %.2f кеВ\n", kin.momentum_ev_c / 1000.0);
        printf("  Довжина хвилі де Бройля: %.6f нм\n", kin.de_broglie_nm);
    }

    return 0;
}
