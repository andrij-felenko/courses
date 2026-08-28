#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Фізичні константи в системі СІ */
#define HBAR 1.054571817e-34     /* Зведена стала Планка, Дж·с */
#define M_E  9.1093837015e-31    /* Маса електрона, кг */
#define KB   1.380649e-23        /* Стала Больцмана, Дж/К */
#define EV   1.602176634e-19     /* 1 електрон-вольт у Джоулях */

/* Густина квантових станів g(E) у 3D просторі */
double density_of_states(double E) {
    if (E <= 0.0) return 0.0;
    double coeff = (1.0 / (2.0 * M_PI * M_PI)) * pow((2.0 * M_E) / (HBAR * HBAR), 1.5);
    return coeff * sqrt(E);
}

/* Функція розподілу Фермі — Дірака f(E) із захистом від переповнення */
double fermi_dirac(double E, double mu, double T) {
    if (T <= 0.0) {
        return (E <= mu) ? 1.0 : 0.0;
    }
    double x = (E - mu) / (KB * T);
    if (x > 100.0) return 0.0;
    if (x < -100.0) return 1.0;
    return 1.0 / (exp(x) + 1.0);
}

/* Чисельне інтегрування густини заповнених станів методом Трапецій */
double integrate_density(double mu, double T, double E_max, int steps) {
    double dE = E_max / steps;
    double sum = 0.5 * (density_of_states(0.0) * fermi_dirac(0.0, mu, T) +
                       density_of_states(E_max) * fermi_dirac(E_max, mu, T));
    for (int i = 1; i < steps; i++) {
        double E = i * dE;
        sum += density_of_states(E) * fermi_dirac(E, mu, T);
    }
    return sum * dE;
}

/* Обчислення об'ємної густини внутрішньої енергії u(T) */
double integrate_energy_density(double mu, double T, double E_max, int steps) {
    double dE = E_max / steps;
    double sum = 0.5 * (0.0 * density_of_states(0.0) * fermi_dirac(0.0, mu, T) +
                       E_max * density_of_states(E_max) * fermi_dirac(E_max, mu, T));
    for (int i = 1; i < steps; i++) {
        double E = i * dE;
        sum += E * density_of_states(E) * fermi_dirac(E, mu, T);
    }
    return sum * dE;
}

/* Пошук хімічного потенціалу mu(T) методом бісекції */
double find_chemical_potential(double n_target, double E_F, double T) {
    if (T <= 0.0) return E_F;
    
    double low = 0.0;
    double high = 2.0 * E_F;
    double E_max = E_F + 10.0 * KB * T;
    int steps = 3000;
    double mu = E_F;

    for (int iter = 0; iter < 60; iter++) {
        mu = 0.5 * (low + high);
        double n_calc = integrate_density(mu, T, E_max, steps);
        if (fabs(n_calc - n_target) / n_target < 1e-7) {
            break;
        }
        if (n_calc < n_target) {
            low = mu;
        } else {
            high = mu;
        }
    }
    return mu;
}

int main(void) {
    /* Концентрація електронів провідності у міді Cu: n = 8.47e28 м^-3 */
    double n = 8.47e28;
    double E_F = (HBAR * HBAR / (2.0 * M_E)) * pow(3.0 * M_PI * M_PI * n, 2.0 / 3.0);
    double T_F = E_F / KB;

    printf("=== МОДЕЛЮВАННЯ ВИРОДЖЕНОГО ЕЛЕКТРОННОГО ГАЗУ (C) ===\n");
    printf("Концентрація електронів n = %.3e m^-3\n", n);
    printf("Енергія Фермі E_F        = %.4f eV\n", E_F / EV);
    printf("Температура Фермі T_F    = %.1f K\n\n", T_F);

    printf("%-8s %-14s %-14s %-18s %-18s\n", 
           "T (K)", "mu (eV)", "mu / E_F", "C_v чисельна", "C_v Зоммерфельд");
    printf("--------------------------------------------------------------------------------\n");

    for (double T = 100.0; T <= 2000.0; T += 300.0) {
        double mu = find_chemical_potential(n, E_F, T);
        
        /* Розрахунок теплоємності чисельним диференціюванням */
        double dT = 2.0;
        double mu_plus = find_chemical_potential(n, E_F, T + dT);
        double mu_minus = find_chemical_potential(n, E_F, T - dT);
        double E_max = E_F + 10.0 * KB * T;
        
        double u_plus = integrate_energy_density(mu_plus, T + dT, E_max, 3000);
        double u_minus = integrate_energy_density(mu_minus, T - dT, E_max, 3000);
        double c_v_num = (u_plus - u_minus) / (2.0 * dT);

        /* Теплоємність за теоретичною формулою Зоммерфельда */
        double c_v_theory = 0.5 * M_PI * M_PI * n * KB * (T / T_F);

        printf("%-8.1f %-14.5f %-14.5f %-18.2f %-18.2f\n", 
               T, mu / EV, mu / E_F, c_v_num, c_v_theory);
    }

    return 0;
}
