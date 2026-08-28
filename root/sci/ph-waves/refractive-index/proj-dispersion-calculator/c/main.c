#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define SPEED_OF_LIGHT_M_S 299792458.0
#define NUM_SELLMEIER_COEFFS 3

typedef struct {
    const char* name;
    double B[NUM_SELLMEIER_COEFFS];
    double C[NUM_SELLMEIER_COEFFS]; /* квадрат резонансних довжин хвиль у мкм² */
    double min_lambda_um;
    double max_lambda_um;
} SellmeierMaterial;

/* Коефіцієнти Селмейєра для оптичного крону N-BK7 (Schott) */
static const SellmeierMaterial MATERIAL_NBK7 = {
    "Schott N-BK7",
    { 1.03961212, 0.231792344, 1.01046945 },
    { 0.00600069867, 0.0200179144, 103.560653 },
    0.300, 2.500
};

/* Коефіцієнти Селмейєра для плавного кварцу (Fused Silica) */
static const SellmeierMaterial MATERIAL_FUSED_SILICA = {
    "Fused Silica (SiO2)",
    { 0.696166300, 0.407942600, 0.897479400 },
    { 0.00467914826, 0.0135120631, 97.9340025 },
    0.210, 3.700
};

/* Коефіцієнти Селмейєра для важкого флінту F2 (Schott) */
static const SellmeierMaterial MATERIAL_F2 = {
    "Schott F2 Flint Glass",
    { 1.34533359, 0.209073176, 0.937357162 },
    { 0.00997743871, 0.0470450767, 111.886764 },
    0.350, 2.000
};

/* Обчислення показника заломлення n(lambda_um) за рівнянням Селмейєра */
double calculate_refractive_index(const SellmeierMaterial* mat, double lambda_um) {
    if (lambda_um < mat->min_lambda_um || lambda_um > mat->max_lambda_um) {
        /* Попередження про вихід за межі діапазону прозорості */
    }
    double lam2 = lambda_um * lambda_um;
    double n2 = 1.0;
    for (int i = 0; i < NUM_SELLMEIER_COEFFS; ++i) {
        double denom = lam2 - mat->C[i];
        if (fabs(denom) < 1e-12) {
            return 0.0; /* Захист від резонансного ділення на нуль */
        }
        n2 += (mat->B[i] * lam2) / denom;
    }
    return sqrt(n2);
}

/* Обчислення першої похідної dn/dλ методом центральних різниць */
double calculate_dn_dlambda(const SellmeierMaterial* mat, double lambda_um, double h_um) {
    double n_plus = calculate_refractive_index(mat, lambda_um + h_um);
    double n_minus = calculate_refractive_index(mat, lambda_um - h_um);
    return (n_plus - n_minus) / (2.0 * h_um);
}

/* Обчислення другого похідної d²n/dλ² методом центральних різниць */
double calculate_d2n_dlambda2(const SellmeierMaterial* mat, double lambda_um, double h_um) {
    double n_center = calculate_refractive_index(mat, lambda_um);
    double n_plus = calculate_refractive_index(mat, lambda_um + h_um);
    double n_minus = calculate_refractive_index(mat, lambda_um - h_um);
    return (n_plus - 2.0 * n_center + n_minus) / (h_um * h_um);
}

/* Обчислення групового показника заломлення n_g */
double calculate_group_index(const SellmeierMaterial* mat, double lambda_um) {
    double n = calculate_refractive_index(mat, lambda_um);
    double dn_dlam = calculate_dn_dlambda(mat, lambda_um, 0.0001);
    return n - lambda_um * dn_dlam;
}

/* Обчислення параметра хроматичної дисперсії D у (пс / (нм · км)) */
double calculate_chromatic_dispersion(const SellmeierMaterial* mat, double lambda_um) {
    double h_um = 0.0005;
    double d2n_dlam2 = calculate_d2n_dlambda2(mat, lambda_um, h_um);
    
    /* D = -(λ/c) * d²n/dλ² */
    double c_um_ps = SPEED_OF_LIGHT_M_S * 1e-6; /* мкм / пс */
    double D_raw = - (lambda_um / c_um_ps) * d2n_dlam2; /* пс / мкм² */
    
    /* Перетворення одиниць: 1 (пс / мкм²) = 1000 (пс / (нм · км)) */
    return D_raw * 1000.0;
}

void print_material_analysis(const SellmeierMaterial* mat) {
    double wavelengths[] = { 0.400, 0.5893, 0.850, 1.310, 1.550 };
    size_t count = sizeof(wavelengths) / sizeof(wavelengths[0]);
    
    printf("\n=== Аналіз спектральної дисперсії: %s ===\n", mat->name);
    printf("λ (мкм)  |   n(λ)   |   n_g(λ)  |  D [пс/(нм·км)] |   v_g (10^8 м/с)\n");
    printf("---------+----------+-----------+-----------------+------------------\n");
    
    for (size_t i = 0; i < count; ++i) {
        double lam = wavelengths[i];
        double n = calculate_refractive_index(mat, lam);
        double ng = calculate_group_index(mat, lam);
        double D = calculate_chromatic_dispersion(mat, lam);
        double vg = SPEED_OF_LIGHT_M_S / ng / 1e8;
        printf("%8.4f | %8.5f | %9.5f | %15.3f | %16.4f\n", lam, n, ng, D, vg);
    }
}

int main(void) {
    print_material_analysis(&MATERIAL_NBK7);
    print_material_analysis(&MATERIAL_FUSED_SILICA);
    print_material_analysis(&MATERIAL_F2);
    return 0;
}
