#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Фізичні фундаментальні константи у системі СІ */
#define CONST_E     1.602176634e-19  /* Елементарний заряд, Кл */
#define CONST_ME    9.1093837015e-31 /* Маса електрона, кг */
#define CONST_HBAR  1.054571817e-34  /* Зведена стала Планка, Дж·с */
#define CONST_EPS0  8.8541878128e-12 /* Електрична стала, Ф/м */

/* Структура параметрів гетероструктури FTJ */
typedef struct {
    double barrier_thickness_nm; /* Товщина d, нм */
    double effective_mass_ratio; /* m* / m_e */
    double phi0_ev;              /* Базова висота бар'єра, еВ */
    double polarization_uc_cm2;  /* Поляризація P, мкКл/см² */
    double lambda1_angstrom;     /* Довжина екранування верхнього електрода, Å */
    double lambda2_angstrom;     /* Довжина екранування нижнього електрода, Å */
    double eps_r;                /* Діелектрична проникність сегнетоелектрика */
} ftj_params_t;

/* Результат розрахунку TER для заданого потенціалу */
typedef struct {
    double v_read;
    double j_on;   /* A/см² */
    double j_off;  /* A/см² */
    double r_on;   /* Ом·см² */
    double r_off;  /* Ом·см² */
    double ter_ratio;
    double ter_percent;
} ftj_result_t;

/* Обчислення електростатичного зсуву висоти бар'єра (в еВ) */
static double calc_barrier_shift_ev(const ftj_params_t *p) {
    double d_m = p->barrier_thickness_nm * 1.0e-9;
    double p_c_m2 = p->polarization_uc_cm2 * 1.0e-2; /* мкКл/см² -> Кл/м² */
    double l1_m = p->lambda1_angstrom * 1.0e-10;
    double l2_m = p->lambda2_angstrom * 1.0e-10;

    double k_scr = (CONST_E / (CONST_EPS0 * p->eps_r)) * 
                   ((l1_m - l2_m) / (d_m + l1_m + l2_m));
    
    double delta_phi_joule = k_scr * p_c_m2;
    return delta_phi_joule / CONST_E; /* Перевід у еВ */
}

/* Густина тунельного струму BDR при напрузі V (в А/см²) */
static double calc_tunnel_current_density(double v_volts, double phi_ev, double d_nm, double m_ratio) {
    if (phi_ev <= 0.01) phi_ev = 0.01; /* Фізичне обмеження на мінімальний бар'єр */

    double d_m = d_nm * 1.0e-9;
    double m_eff = m_ratio * CONST_ME;
    double phi_j = phi_ev * CONST_E;
    double v_j = fabs(v_volts) * CONST_E;

    /* Коефіцієнт згасання A = (2 * sqrt(2 * m*)) / hbar */
    double a_const = (2.0 * sqrt(2.0 * m_eff)) / CONST_HBAR;

    /* Ефективна висота бар'єра з урахуванням похилу від напруги */
    double phi_eff = phi_j - v_j / 2.0;
    if (phi_eff <= 0.001 * CONST_E) phi_eff = 0.001 * CONST_E;

    /* Тунельний коефіцієнт проходження D */
    double d_factor = exp(-a_const * d_m * sqrt(phi_eff));

    /* Ампер-вольтний коефіцієнт C0 (у А/м²) */
    double c0 = (CONST_E * CONST_E * sqrt(2.0 * m_eff)) / 
                (4.0 * M_PI * M_PI * CONST_HBAR * CONST_HBAR * d_m);

    double j_a_m2 = c0 * v_volts * sqrt(phi_eff / CONST_E) * d_factor;
    return (j_a_m2 * 1.0e-4); /* А/м² -> А/см² */
}

/* Симуляція осередку FTJ при читанні */
ftj_result_t simulate_ftj_read(const ftj_params_t *p, double v_read) {
    ftj_result_t res;
    res.v_read = v_read;

    double delta_phi = calc_barrier_shift_ev(p);
    double phi_on = p->phi0_ev - delta_phi;
    double phi_off = p->phi0_ev + delta_phi;

    res.j_on = calc_tunnel_current_density(v_read, phi_on, p->barrier_thickness_nm, p->effective_mass_ratio);
    res.j_off = calc_tunnel_current_density(v_read, phi_off, p->barrier_thickness_nm, p->effective_mass_ratio);

    res.r_on = (res.j_on > 0.0) ? (v_read / res.j_on) : 1.0e12;
    res.r_off = (res.j_off > 0.0) ? (v_read / res.j_off) : 1.0e12;

    res.ter_ratio = (res.j_off > 0.0) ? (res.j_on / res.j_off) : 1.0;
    res.ter_percent = (res.ter_ratio - 1.0) * 100.0;

    return res;
}

int main(void) {
    ftj_params_t cell = {
        .barrier_thickness_nm = 2.0,
        .effective_mass_ratio = 0.5,
        .phi0_ev = 1.2,
        .polarization_uc_cm2 = 20.0,
        .lambda1_angstrom = 0.8,
        .lambda2_angstrom = 0.2,
        .eps_r = 25.0
    };

    printf("=== Симуляція FTJ (C-реалізація) ===\n");
    printf("Товщина d = %.2f нм, P = %.1f мкКл/см²\n", cell.barrier_thickness_nm, cell.polarization_uc_cm2);
    printf("Довжини екранування: λ1 = %.1f Å, λ2 = %.1f Å\n\n", cell.lambda1_angstrom, cell.lambda2_angstrom);

    printf("V_read (В)  | J_ON (А/см²)  | J_OFF (А/см²) | R_ON (Ом·см²) | R_OFF (Ом·см²) | TER (%)\n");
    printf("---------------------------------------------------------------------------------------\n");

    for (double v = 0.01; v <= 0.10; v += 0.02) {
        ftj_result_t r = simulate_ftj_read(&cell, v);
        printf("%10.2f  | %13.3e | %13.3e | %13.3e | %13.3e | %10.1f%%\n",
               r.v_read, r.j_on, r.j_off, r.r_on, r.r_off, r.ter_percent);
    }

    return 0;
}
