#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Фундаментальні фізичні константи (CODATA) */
#define CONST_R_INF     10973731.568160  /* Стала Рідберга для нескінченної маси (м⁻¹) */
#define CONST_MASS_E    9.1093837015e-31 /* Маса електрона (кг) */
#define CONST_MASS_P    1.67262192369e-27/* Маса протона (кг) */
#define CONST_MASS_D    3.3435837724e-27 /* Маса дейтерону (кг) */
#define CONST_ALPHA     7.2973525693e-3  /* Стала тонкої структури α ≈ 1/137 */
#define CONST_C         299792458.0      /* Швидкість світла у вакуумі (м/с) */
#define CONST_EV_JOULE  1.602176634e-19  /* Джоулів у 1 еВ */
#define CONST_PLANCK    6.62607015e-34   /* Стала Планка h (Дж·с) */

typedef struct {
    const char *name;
    double nuclear_mass_kg;
    int Z;
} HydrogenIsotope;

typedef struct {
    int n1;
    int n2;
    double wavelength_vac_nm;
    double wavelength_air_nm;
    double energy_ev;
} SpectralLineResult;

/* Обчислення ефективної сталої Рідберга з урахуванням маси ядра */
double get_reduced_rydberg(double nuclear_mass_kg, int Z) {
    double reduced_mass_ratio = 1.0 / (1.0 + CONST_MASS_E / nuclear_mass_kg);
    return CONST_R_INF * ((double)Z * (double)Z) * reduced_mass_ratio;
}

/* Формула Едлена для показника заломлення стандартного повітря */
double air_refractive_index(double lambda_vac_nm) {
    if (lambda_vac_nm <= 0.0) return 1.0;
    double sigma = 1000.0 / lambda_vac_nm; /* Хвильове число в мкм⁻¹ */
    double s2 = sigma * sigma;
    double n_minus_1 = 1.0e-8 * (8342.54 + 2406147.0 / (130.0 - s2) + 15998.0 / (38.9 - s2));
    return 1.0 + n_minus_1;
}

/* Обчислення параметрів спектральної лінії між рівнями n1 та n2 */
int compute_spectral_line(const HydrogenIsotope *iso, int n1, int n2, SpectralLineResult *out_line) {
    if (!iso || !out_line || n1 <= 0 || n2 <= n1) {
        return -1;
    }

    double R_eff = get_reduced_rydberg(iso->nuclear_mass_kg, iso->Z);
    double wavenumber = R_eff * (1.0 / ((double)n1 * n1) - 1.0 / ((double)n2 * n2));

    if (wavenumber <= 0.0) return -2;

    double lambda_vac_m = 1.0 / wavenumber;
    double lambda_vac_nm = lambda_vac_m * 1.0e9;
    double n_air = air_refractive_index(lambda_vac_nm);
    double lambda_air_nm = lambda_vac_nm / n_air;

    double energy_j = wavenumber * CONST_PLANCK * CONST_C;
    double energy_ev = energy_j / CONST_EV_JOULE;

    out_line->n1 = n1;
    out_line->n2 = n2;
    out_line->wavelength_vac_nm = lambda_vac_nm;
    out_line->wavelength_air_nm = lambda_air_nm;
    out_line->energy_ev = energy_ev;

    return 0;
}

/* Релятивістський зсув Дірака для стану (n, j) у електронвольтах */
double dirac_fine_structure_shift_ev(int Z, int n, double j) {
    if (n <= 0 || j < 0.5) return 0.0;
    
    double Z_alpha = (double)Z * CONST_ALPHA;
    double Z_alpha2 = Z_alpha * Z_alpha;
    double E_n = -13.605693 * ((double)(Z * Z) / ((double)(n * n)));
    double factor = (Z_alpha2 / ((double)n)) * ((1.0 / (j + 0.5)) - (0.75 / (double)n));
    
    return E_n * factor;
}

int main(void) {
    HydrogenIsotope protium = {"Протій (1H)", CONST_MASS_P, 1};
    HydrogenIsotope deuterium = {"Дейтерій (2H)", CONST_MASS_D, 1};

    printf("=== Спектральні лінії серії Бальмера (C) ===\n\n");
    printf("%-15s %-6s %-14s %-14s %-12s\n", "Ізотоп", "Перехід", "λ вак (нм)", "λ повітря (нм)", "ΔE (еВ)");
    printf("--------------------------------------------------------------------\n");

    for (int n2 = 3; n2 <= 6; ++n2) {
        SpectralLineResult res_h, res_d;
        if (compute_spectral_line(&protium, 2, n2, &res_h) == 0 &&
            compute_spectral_line(&deuterium, 2, n2, &res_d) == 0) {
            
            printf("%-15s %d -> %d  %-14.4f %-14.4f %-12.4f\n", 
                   protium.name, res_h.n1, res_h.n2, res_h.wavelength_vac_nm, res_h.wavelength_air_nm, res_h.energy_ev);
            printf("%-15s %d -> %d  %-14.4f %-14.4f %-12.4f\n", 
                   deuterium.name, res_d.n1, res_d.n2, res_d.wavelength_vac_nm, res_d.wavelength_air_nm, res_d.energy_ev);
            
            double shift_pm = (res_h.wavelength_vac_nm - res_d.wavelength_vac_nm) * 1000.0;
            printf("  └─ Ізотопічний зсув H-D: %.2f пм (%.4f нм)\n\n", shift_pm, shift_pm / 1000.0);
        }
    }

    printf("\n=== Тонке розщеплення рівня n = 2 в атомі водню ===\n");
    double shift_2s12 = dirac_fine_structure_shift_ev(1, 2, 0.5);
    double shift_2p32 = dirac_fine_structure_shift_ev(1, 2, 1.5);
    printf("Зсув рівня 2S_1/2 (j = 1/2): %+.6e еВ\n", shift_2s12);
    printf("Зсув рівня 2P_3/2 (j = 3/2): %+.6e еВ\n", shift_2p32);
    printf("Тонкий інтервал 2P_3/2 - 2S_1/2: %.6e еВ (%.2f МГц)\n", 
           fabs(shift_2p32 - shift_2s12), fabs(shift_2p32 - shift_2s12) * CONST_EV_JOULE / (CONST_PLANCK * 1e6));

    return 0;
}
