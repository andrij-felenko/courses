#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Фізичні константи в системі СІ */
#define Q_ELEM    1.602176634e-19 /* Заряд електрона, Кл */
#define K_BOLTZ   1.380649e-23    /* Стала Больцмана, Дж/К */
#define EPS_0     8.854187817e-12 /* Електрична стала, Ф/м */
#define H_PLANCK  6.62607015e-34  /* Стала Планка, Дж·с */

/* Структура параметрів контакту Шотткі */
typedef struct {
    double phi_bn0;    /* Початкова висота бар'єра при нульовому зміщенні, еВ */
    double n_d;        /* Концентрація донорів в напівпровіднику, м⁻³ */
    double eps_r;      /* Відносна діелектрична проникність */
    double m_eff_rel;  /* Відносна ефективна маса електрона m*/m0 */
    double temp_k;     /* Абсолютна температура, К */
    double area_m2;    /* Площа контакту, м² */
    double r_series;   /* Послідовний опір об'єму напівпровідника, Ом */
} schottky_contact_t;

/* Обчислення ефективної сталої Річардсона A**, А/(м²·К²) */
static double calc_richardson_constant(double m_eff_rel) {
    const double m0 = 9.1093837015e-31;
    double m_eff = m_eff_rel * m0;
    return (4.0 * M_PI * Q_ELEM * m_eff * K_BOLTZ * K_BOLTZ) / (H_PLANCK * H_PLANCK * H_PLANCK);
}

/* Обчислення струму діода Шотткі за зовнішньою напругою v_ext методом Ньютона-Рафсона */
static double calc_diode_current(const schottky_contact_t *c, double v_ext) {
    double a_star = calc_richardson_constant(c->m_eff_rel);
    double vt = (K_BOLTZ * c->temp_k) / Q_ELEM;
    
    /* Струм насичення J_s, А/м² */
    double j_s = a_star * c->temp_k * c->temp_k * exp(-c->phi_bn0 / vt);
    double i_s = j_s * c->area_m2;
    
    /* Ітераційний пошук v_d (напруги безпосередньо на бар'єрі) */
    double v_d = v_ext;
    const int max_iter = 100;
    const double tol = 1e-12;
    
    for (int iter = 0; iter < max_iter; iter++) {
        /* Ефект Шотткі: зниження бар'єра дзеркальними силами */
        double v_bi = c->phi_bn0; /* Наближення вбудованого потенціалу */
        double e_max = 0.0;
        if (v_bi > v_d) {
            e_max = sqrt((2.0 * Q_ELEM * c->n_d * (v_bi - v_d)) / (c->eps_r * EPS_0));
        }
        double delta_phi = sqrt((Q_ELEM * e_max) / (4.0 * M_PI * c->eps_r * EPS_0));
        double n_eff = 1.0 + (delta_phi / (2.0 * v_bi)); /* Ефективний коефіцієнт неідеальності */

        double current_calc = i_s * (exp(v_d / (n_eff * vt)) - 1.0);
        double f_val = v_d + current_calc * c->r_series - v_ext;
        
        double df_dvd = 1.0 + (current_calc + i_s) * (c->r_series / (n_eff * vt));
        double v_d_next = v_d - f_val / df_dvd;
        
        if (fabs(v_d_next - v_d) < tol) {
            v_d = v_d_next;
            break;
        }
        v_d = v_d_next;
    }
    
    return i_s * (exp(v_d / (1.02 * vt)) - 1.0);
}

/* Обчислення питомого опору контакту rho_c у режимі квантового тунелювання (FE), Ом·см² */
static double calc_specific_contact_resistance(double phi_bn_ev, double n_d_cm3, double m_eff_rel, double eps_r) {
    const double hbar = 1.054571817e-34;
    const double m0 = 9.1093837015e-31;
    
    double n_d_m3 = n_d_cm3 * 1.0e6;
    double m_eff = m_eff_rel * m0;
    double eps_s = eps_r * EPS_0;
    
    /* Характеристична тунельна енергія Падовані-Стратона E_00, Дж */
    double e_00 = (Q_ELEM * hbar / 2.0) * sqrt(n_d_m3 / (m_eff * eps_s));
    double e_00_ev = e_00 / Q_ELEM;
    
    /* Питомий опір у режимі FE (в Ом·м²) */
    double rho_c_m2 = exp((phi_bn_ev) / e_00_ev);
    
    /* Переведення в Ом·см² з нормованою відносною константою */
    return rho_c_m2 * 1.0e4 * 1.0e-11;
}

int main(void) {
    schottky_contact_t diode = {
        .phi_bn0 = 0.75,      /* Бар'єр 0.75 еВ (типово для Ni/Si) */
        .n_d = 1.0e22,        /* 1e16 см⁻³ = 1e22 м⁻³ */
        .eps_r = 11.7,        /* Кремній */
        .m_eff_rel = 0.26,    /* Ефективна маса в Si */
        .temp_k = 300.0,      /* 300 К */
        .area_m2 = 1.0e-8,    /* Площа 100 мкм x 100 мкм */
        .r_series = 15.0      /* Опір 15 Ом */
    };
    
    printf("=== МОДЕЛЮВАННЯ ВАХ КОНТАКТУ МЕТАЛ-НАПІВПРОВІДНИК (C) ===\n");
    printf("Напруга V (В) | Струм I (мА)\n");
    printf("-------------------------------\n");
    
    for (double v = -0.5; v <= 0.61; v += 0.1) {
        double i_amp = calc_diode_current(&diode, v);
        printf("    %5.2f     |   %10.4e\n", v, i_amp * 1000.0);
    }
    
    printf("\n=== РОЗРАХУНОК ПИТОМОГО ОПОРУ ТУНЕЛЬНОГО КОНТАКТУ ===\n");
    printf("Легування N_d (см⁻³) | Питомий опір rho_c (Ом·см²)\n");
    printf("-------------------------------------------------\n");
    double conc[] = {1.0e17, 1.0e18, 1.0e19, 1.0e20};
    for (int i = 0; i < 4; i++) {
        double rho_c = calc_specific_contact_resistance(0.65, conc[i], 0.26, 11.7);
        printf("      %.1e        |        %10.3e\n", conc[i], rho_c);
    }
    
    return 0;
}
