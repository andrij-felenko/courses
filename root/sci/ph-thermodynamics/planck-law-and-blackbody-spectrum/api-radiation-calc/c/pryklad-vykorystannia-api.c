#include <stdio.h>
#include "blackbody_radiation.h"

int main(void) {
    double T = 5778.0; /* Ефективна температура Сонця */
    double radiance = 0.0;
    double lambda_peak = 0.0;

    /* Обчислення яскравості на довжині хвилі 500 нм */
    bb_status_t status = bb_spectral_radiance(500.0e-9, T, &radiance);
    if (status != BB_SUCCESS) {
        printf("Помилка обчислення: %d\n", status);
        return 1;
    }

    bb_wien_peak(T, &lambda_peak);
    printf("Спектральна яскравість на 500 нм: %.3e Вт/(м²·ст·м)\n", radiance);
    printf("Пік випромінювання Віна:          %.2f нм\n", lambda_peak * 1.0e9);

    /* Інтегрування у видимому діапазоні (380 - 780 нм) */
    bb_integration_config_t cfg = {
        .max_subintervals = 2000,
        .rel_tolerance = 1.0e-6,
        .abs_tolerance = 1.0e-10,
        .use_gauss_legendre = true
    };
    bb_band_result_t res;
    if (bb_integrate_band(T, 380.0e-9, 780.0e-9, &cfg, &res) == BB_SUCCESS) {
        printf("Потужність у видимому спектрі:   %.2f Вт/м²\n", res.integrated_emittance);
    }

    return 0;
}
