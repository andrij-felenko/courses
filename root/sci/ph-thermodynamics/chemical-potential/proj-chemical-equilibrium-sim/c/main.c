#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define KB_EV 8.617333262e-5  /* Константа Больцмана в ев/К */
#define PI 3.14159265358979323846

/* Структура для параметрів електронного газу */
typedef struct {
    double fermi_energy_ev; /* Енергія Фермі при 0 К (ев) */
    double temperature_k;   /* Температура (К) */
} FermiGas;

/* Розрахунок хімічного потенціалу Фермі-газу (ев) */
double fermi_chemical_potential(const FermiGas *gas) {
    if (gas->temperature_k <= 0.0) {
        return gas->fermi_energy_ev;
    }
    
    double kt = KB_EV * gas->temperature_k;
    double ratio = kt / gas->fermi_energy_ev;
    
    /* Квадратична та четвертна поправка Зоммерфельда */
    double term2 = (PI * PI / 12.0) * ratio * ratio;
    double term4 = (PI * PI * PI * PI / 80.0) * pow(ratio, 4.0);
    
    return gas->fermi_energy_ev * (1.0 - term2 - term4);
}

/* Структура фазової рівноваги рідина-пара */
typedef struct {
    double temp_k;            /* Температура (К) */
    double molar_mass_kg;     /* Молярна маса (кг/моль) */
    double heat_vap_j_mol;    /* Питома теплота випаровування (Дж/моль) */
    double ref_temp_k;        /* Опорна температура (К) */
    double ref_press_pa;      /* Опорний тиск (Па) */
} PhaseEquilibrium;

/* Обчислення тиску насиченої пари з рівняння Клапейрона-Клаузіуса (Па) */
double calculate_saturation_pressure(const PhaseEquilibrium *eq) {
    const double R = 8.314462618; /* Універсальна газова стала */
    
    /* Інтегрування рівняння d(μ_vap - μ_liq) = 0 при стрімкій теплоті випаровування */
    double exponent = (eq->heat_vap_j_mol / R) * (1.0 / eq->ref_temp_k - 1.0 / eq->temp_k);
    return eq->ref_press_pa * exp(exponent);
}

int main(void) {
    printf("=== Чисельний розрахунок хімічного потенціалу ===\n\n");
    
    /* 1. Обчислення μ(T) для електронів у міді (E_F = 7.0 eV) */
    FermiGas copper = { .fermi_energy_ev = 7.00, .temperature_k = 300.0 };
    double mu_300 = fermi_chemical_potential(&copper);
    
    copper.temperature_k = 1000.0;
    double mu_1000 = fermi_chemical_potential(&copper);
    
    printf("Електрони у міді (E_F = 7.000 eV):\n");
    printf("  T = 300 K:  μ = %.6f eV  (Δμ = %.6f eV)\n", mu_300, mu_300 - 7.0);
    printf("  T = 1000 K: μ = %.6f eV  (Δμ = %.6f eV)\n\n", mu_1000, mu_1000 - 7.0);
    
    /* 2. Рівноважний тиск випаровування води при T = 373.15 K (100 °C) та 323.15 K (50 °C) */
    PhaseEquilibrium water = {
        .temp_k = 323.15,
        .molar_mass_kg = 0.018015,
        .heat_vap_j_mol = 40650.0,
        .ref_temp_k = 373.15,
        .ref_press_pa = 101325.0
    };
    
    double p_sat_50c = calculate_saturation_pressure(&water);
    printf("Фазова рівновага води (H2O):\n");
    printf("  T = 100 °C: P_sat = %.1f Pa  (1.00 atm)\n", water.ref_press_pa);
    printf("  T = 50 °C:  P_sat = %.1f Pa  (%.3f atm)\n", p_sat_50c, p_sat_50c / 101325.0);
    
    return 0;
}
