#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура паспортних параметрів одновісного кристала */
typedef struct {
    double n_o;        /* Звичайний показник заломлення */
    double n_e;        /* Головний незвичайний показник заломлення */
    const char* name;  /* Текстова назва кристалічного матеріалу */
} UniaxialCrystal;

/* Результати аналізу двозаломлення для конкретного променя */
typedef struct {
    double theta_deg;   /* Кут між хвильовим вектором та оптичною віссю (градуси) */
    double n_e_theta;   /* Ефективний показник заломлення e-променя */
    double walkoff_deg; /* Кут зносу Пойнтінга (градуси) */
    double shift_um;    /* Просторовий зсув e-променя (мікрометри) */
    double ret_rad;     /* Набіг різниці фаз (радіани) */
    double ret_deg;     /* Набіг різниці фаз (градуси) */
} BirefringenceResult;

/* Обчислення параметрів двозаломлення */
BirefringenceResult calculate_birefringence(const UniaxialCrystal* crystal,
                                           double theta_deg,
                                           double thickness_mm,
                                           double wavelength_nm) {
    BirefringenceResult res;
    res.theta_deg = theta_deg;

    /* Перехід до радіан */
    double theta = theta_deg * M_PI / 180.0;
    double cos_t = cos(theta);
    double sin_t = sin(theta);
    double tan_t = tan(theta);

    /* 1. Ефективний показник заломлення n_e(theta) */
    double no2 = crystal->n_o * crystal->n_o;
    double ne2 = crystal->n_e * crystal->n_e;
    double denom = sqrt(ne2 * cos_t * cos_t + no2 * sin_t * sin_t);
    res.n_e_theta = (crystal->n_o * crystal->n_e) / denom;

    /* 2. Кут зносу Пойнтінга eta */
    double eta = 0.0;
    if (fabs(cos_t) > 1e-12 && fabs(sin_t) > 1e-12) {
        eta = atan(((no2 - ne2) * tan_t) / (no2 + ne2 * tan_t * tan_t));
    }
    res.walkoff_deg = eta * 180.0 / M_PI;

    /* 3. Просторовий зсув променя (у мікрометрах) */
    double d_um = thickness_mm * 1000.0;
    res.shift_um = d_um * tan(fabs(eta));

    /* 4. Фазове запізнення */
    double delta_n = fabs(res.n_e_theta - crystal->n_o);
    double lambda_mm = wavelength_nm * 1e-6;
    res.ret_rad = (2.0 * M_PI / lambda_mm) * thickness_mm * delta_n;
    res.ret_deg = fmod(res.ret_rad * 180.0 / M_PI, 360.0);

    return res;
}

/* Друк таблиці аналізу */
void print_birefringence_table(const UniaxialCrystal* crystal,
                               double thickness_mm,
                               double wavelength_nm) {
    printf("=========================================================================\n");
    printf(" МАТЕРІАЛ: %s\n", crystal->name);
    printf(" Параметри: n_o = %.4f, n_e = %.4f, Δn_max = %+.4f\n",
           crystal->n_o, crystal->n_e, crystal->n_e - crystal->n_o);
    printf(" Умови: Товщина = %.1f мм, Довжина хвилі = %.1f нм\n", thickness_mm, wavelength_nm);
    printf("=========================================================================\n");
    printf(" Кут θ (°) |  n_e(θ)   | Знос η (°) | Зсув Δ (мкм) | Фаза (рад) | Фаза (°) \n");
    printf("-----------+-----------+------------+--------------+------------+----------\n");

    for (int deg = 0; deg <= 90; deg += 10) {
        BirefringenceResult r = calculate_birefringence(crystal, (double)deg, thickness_mm, wavelength_nm);
        printf("    %2d     |  %.6f |   %6.3f   |   %8.2f   | %10.2f |  %6.1f \n",
               deg, r.n_e_theta, r.walkoff_deg, r.shift_um, r.ret_rad, r.ret_deg);
    }
    printf("-------------------------------------------------------------------------\n\n");
}

int main(void) {
    /* Кальцит (одновісний негативний) */
    UniaxialCrystal calcite = {1.6580, 1.4864, "Кальцит (CaCO3) - Негативний"};
    /* Кварц (одновісний позитивний) */
    UniaxialCrystal quartz = {1.5426, 1.5517, "Кварц (SiO2) - Позитивний"};

    double thickness = 10.0;   /* 10 мм */
    double wavelength = 632.8;  /* Гелій-неоновий лазер */

    print_birefringence_table(&calcite, thickness, wavelength);
    print_birefringence_table(&quartz, thickness, wavelength);

    return 0;
}
