#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define SPECTRUM_START 380
#define SPECTRUM_END   780
#define SPECTRUM_STEP  10
#define NUM_BANDS      ((SPECTRUM_END - SPECTRUM_START) / SPECTRUM_STEP + 1)

typedef struct {
    double wavelength_nm;
    double beta_scattering; /* м^-1 */
    double optical_depth;   /* τ_R в зеніті */
    double transmittance;   /* T(λ) при заданому air_mass */
} SpectrumPoint;

typedef struct {
    double r, g, b;
} RGBColor;

/* Спрощені функції колірної відповідності CIE 1931 (XYZ) */
static void get_cie_xyz(double wl_nm, double *x, double *y, double *z) {
    double w = wl_nm;
    *x = 1.056 * exp(-0.5 * pow((w - 595.0) / 42.0, 2.0)) +
         0.362 * exp(-0.5 * pow((w - 442.0) / 22.0, 2.0));
    *y = 1.011 * exp(-0.5 * pow((w - 556.0) / 48.0, 2.0));
    *z = 2.065 * exp(-0.5 * pow((w - 447.0) / 21.0, 2.0));
}

/* Обчислення показника заломлення повітря (формула Едлена) */
static double air_refractive_index(double wl_nm) {
    double wl_um = wl_nm / 1000.0;
    double sigma2 = 1.0 / (wl_um * wl_um);
    double n_minus_1 = 8342.54 + 2406147.0 / (130.0 - sigma2) + 15998.0 / (38.9 - sigma2);
    return 1.0 + n_minus_1 * 1e-8;
}

/* Розрахунок коефіцієнта релеєвського розсіяння */
static double calculate_rayleigh_beta(double wl_nm) {
    double lambda_m = wl_nm * 1e-9;
    double n = air_refractive_index(wl_nm);
    double N_s = 2.547e25; /* м^-3 */
    double F_K = 1.061;    /* Коефіцієнт Кабанна */
    
    double n2_minus_1 = n * n - 1.0;
    double PI = 3.14159265358979323846;
    
    double beta = (8.0 * pow(PI, 3.0) * pow(n2_minus_1, 2.0)) / 
                 (3.0 * N_s * pow(lambda_m, 4.0)) * F_K;
    return beta;
}

/* Перетворення градусів XYZ у простір sRGB */
static RGBColor xyz_to_srgb(double X, double Y, double Z) {
    double r_lin =  3.2406 * X - 1.5372 * Y - 0.4986 * Z;
    double g_lin = -0.9689 * X + 1.8758 * Y + 0.0415 * Z;
    double b_lin =  0.0557 * X - 0.2040 * Y + 1.0570 * Z;

    RGBColor col;
    col.r = (r_lin <= 0.0031308) ? 12.92 * r_lin : 1.055 * pow(r_lin, 1.0 / 2.4) - 0.055;
    col.g = (g_lin <= 0.0031308) ? 12.92 * g_lin : 1.055 * pow(g_lin, 1.0 / 2.4) - 0.055;
    col.b = (b_lin <= 0.0031308) ? 12.92 * b_lin : 1.055 * pow(b_lin, 1.0 / 2.4) - 0.055;

    if (col.r < 0.0) col.r = 0.0; if (col.r > 1.0) col.r = 1.0;
    if (col.g < 0.0) col.g = 0.0; if (col.g > 1.0) col.g = 1.0;
    if (col.b < 0.0) col.b = 0.0; if (col.b > 1.0) col.b = 1.0;

    return col;
}

int main(void) {
    double air_mass = 1.5; /* Стандартна сонячна інсоляція AM1.5 */
    double scale_height_m = 8500.0; /* H_p */

    SpectrumPoint spectrum[NUM_BANDS];
    double X = 0.0, Y = 0.0, Z = 0.0;

    printf("=== Спектральний розрахунок Релея (Air Mass = %.1f) ===\n", air_mass);
    printf("Довжина хвилі (нм) | β_R (1/км) |  Оптична товщина τ | Пропущення T(λ)\n");
    printf("-----------------------------------------------------------------------\n");

    for (int i = 0; i < NUM_BANDS; ++i) {
        double wl = SPECTRUM_START + i * SPECTRUM_STEP;
        spectrum[i].wavelength_nm = wl;
        spectrum[i].beta_scattering = calculate_rayleigh_beta(wl);
        spectrum[i].optical_depth = spectrum[i].beta_scattering * scale_height_m;
        spectrum[i].transmittance = exp(-spectrum[i].optical_depth * air_mass);

        double cx, cy, cz;
        get_cie_xyz(wl, &cx, &cy, &cz);
        X += spectrum[i].transmittance * cx * SPECTRUM_STEP;
        Y += spectrum[i].transmittance * cy * SPECTRUM_STEP;
        Z += spectrum[i].transmittance * cz * SPECTRUM_STEP;

        if (i % 5 == 0) {
            printf("      %3.0f нм      | %10.4f |     %12.4f |    %12.4f%%\n",
                   wl, spectrum[i].beta_scattering * 1e3,
                   spectrum[i].optical_depth, spectrum[i].transmittance * 100.0);
        }
    }

    double max_val = (X > Y) ? ((X > Z) ? X : Z) : ((Y > Z) ? Y : Z);
    if (max_val > 0.0) { X /= max_val; Y /= max_val; Z /= max_val; }

    RGBColor rgb = xyz_to_srgb(X, Y, Z);
    printf("-----------------------------------------------------------------------\n");
    printf("Підсумковий RGB колір диска Сонця: R = %.3f, G = %.3f, B = %.3f\n",
           rgb.r, rgb.g, rgb.b);

    return 0;
}
