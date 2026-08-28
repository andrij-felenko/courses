/* c */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define K_B_EV 8.61733324e-5  /* Константа Больцмана в еВ/К */
#define T_ROOM 300.0          /* Кімнатна температура 300 K */

typedef struct {
    const char* name;
    double e_g;            /* Ширина забороненої зони (еВ) */
    int is_direct;         /* 1 - прямозонний, 0 - непрямозонний */
    double const_coeff;    /* Коефіцієнт A_dir або B_ind */
    double e_phonon;       /* Енергія фонона для непрямого (еВ) */
    double e_g_direct_sec; /* Енергія прямого переходу для непрямого (еВ) */
} Semiconductor;

/* Обчислення коефіцієнта поглинання alpha (в см^-1) */
double calculate_alpha(const Semiconductor* semi, double photon_energy_ev) {
    /* Нижче порогу поглинання немає */
    if (photon_energy_ev < semi->e_g && semi->is_direct) {
        return 0.0;
    }

    if (semi->is_direct) {
        /* Прямий перехід: alpha = A * sqrt(h*nu - E_g) */
        double delta_e = photon_energy_ev - semi->e_g;
        return semi->const_coeff * sqrt(delta_e);
    } else {
        /* Враховуємо перемикання на прямий перехід при високих енергіях (для Si при > 3.4 еВ) */
        if (semi->e_g_direct_sec > 0.0 && photon_energy_ev >= semi->e_g_direct_sec) {
            double delta_dir = photon_energy_ev - semi->e_g_direct_sec;
            return 2.5e4 + 6.0e4 * sqrt(delta_dir);
        }

        /* Непрямий перехід з випромінюванням і поглинанням фононів */
        double alpha = 0.0;
        double h_omega = semi->e_phonon;
        double kt = K_B_EV * T_ROOM;

        /* Гілка з поглинанням фонона: h*nu >= E_g - h_omega */
        if (photon_energy_ev >= (semi->e_g - h_omega)) {
            double delta_abs = photon_energy_ev - semi->e_g + h_omega;
            double arg = h_omega / kt;
            double n_q = (arg < 80.0) ? (1.0 / (exp(arg) - 1.0)) : 0.0;
            alpha += semi->const_coeff * delta_abs * delta_abs * n_q;
        }

        /* Гілка з випромінюванням фонона: h*nu >= E_g + h_omega */
        if (photon_energy_ev >= (semi->e_g + h_omega)) {
            double delta_em = photon_energy_ev - semi->e_g - h_omega;
            double arg = -h_omega / kt;
            double n_q_plus_1 = (arg > -80.0) ? (1.0 / (1.0 - exp(arg))) : 1.0;
            alpha += semi->const_coeff * delta_em * delta_em * n_q_plus_1;
        }

        return alpha;
    }
}

/* Обчислення товщини в мікрометрах (мкм), необхідної для 95% поглинання */
double calculate_thickness_95_um(double alpha_cm1) {
    if (alpha_cm1 <= 1e-6) {
        return 1e9; /* Практично не поглинає */
    }
    double d_cm = log(20.0) / alpha_cm1;
    return d_cm * 1e4; /* Переведення см -> мкм */
}

int main(void) {
    Semiconductor semiconductors[] = {
        {"Арсенід галію (GaAs)", 1.42, 1, 4.5e4, 0.0,   0.0},
        {"Нітрид галію (GaN)",   3.40, 1, 1.2e5, 0.0,   0.0},
        {"Кремній (Si)",         1.12, 0, 3.2e3, 0.051, 3.40},
        {"Германій (Ge)",        0.66, 0, 2.8e3, 0.028, 0.80}
    };
    size_t num_semis = sizeof(semiconductors) / sizeof(semiconductors[0]);

    double energies[] = {1.2, 1.4, 1.5, 1.8, 2.0, 2.5, 3.5};
    size_t num_energies = sizeof(energies) / sizeof(energies[0]);

    printf("%-22s | %-8s | %-12s | %-15s\n", "Матеріал", "h*nu (еВ)", "alpha (см^-1)", "d_95% (мкм)");
    printf("-------------------------------------------------------------------\n");

    for (size_t i = 0; i < num_energies; ++i) {
        double e_photon = energies[i];

        for (size_t s = 0; s < num_semis; ++s) {
            double alpha = calculate_alpha(&semiconductors[s], e_photon);
            double d_95 = calculate_thickness_95_um(alpha);

            if (alpha > 0.0) {
                printf("%-22s | %8.2f | %12.1f | %15.2f\n",
                       semiconductors[s].name, e_photon, alpha, d_95);
            } else {
                printf("%-22s | %8.2f | %12s | %15s\n",
                       semiconductors[s].name, e_photon, "0.0 (прозорий)", "N/A");
            }
        }
        printf("-------------------------------------------------------------------\n");
    }

    return 0;
}
