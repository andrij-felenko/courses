/* main_igrf.c - Реалізація та демо-обчислення геомагнітного поля у Київській області */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "igrf_model.h"

int igrf_calculate(const GeodeticCoord* coord, const IGRFCoefficients* coeffs, MagneticVector* result) {
    if (!coord || !coeffs || !result) return -1;
    if (coord->latitude_deg < -90.0 || coord->latitude_deg > 90.0) return -2;

    /* Спрощений дипольний розрахунок для головних коефіцієнтів g10, g11, h11 */
    double g10 = coeffs->g[1][0]; /* ~ -29400 нТл */
    double g11 = coeffs->g[1][1]; /* ~ -1450 нТл */
    double h11 = coeffs->h[1][1]; /* ~ 4650 нТл */

    double lat_rad = coord->latitude_deg * (M_PI / 180.0);
    double lon_rad = coord->longitude_deg * (M_PI / 180.0);
    double r = 6371.2 + coord->altitude_km;
    double r_ratio = 6371.2 / r;
    double r_factor = r_ratio * r_ratio * r_ratio;

    double colat = (90.0 - coord->latitude_deg) * (M_PI / 180.0);

    /* Радіальна та меридіональна компоненти диполя */
    double Br = 2.0 * r_factor * (g10 * cos(colat) + (g11 * cos(lon_rad) + h11 * sin(lon_rad)) * sin(colat));
    double Bt = -r_factor * (-g10 * sin(colat) + (g11 * cos(lon_rad) + h11 * sin(lon_rad)) * cos(colat));
    double Bp = (r_factor / sin(colat)) * (-g11 * sin(lon_rad) + h11 * cos(lon_rad)) * sin(colat);

    /* Перетворення до географічної системи X (Північ), Y (Схід), Z (Вниз) */
    result->X_nT = -Bt;
    result->Y_nT = Bp;
    result->Z_nT = -Br;

    result->H_nT = sqrt(result->X_nT * result->X_nT + result->Y_nT * result->Y_nT);
    result->F_nT = sqrt(result->H_nT * result->H_nT + result->Z_nT * result->Z_nT);
    result->D_deg = atan2(result->Y_nT, result->X_nT) * (180.0 / M_PI);
    result->I_deg = atan2(result->Z_nT, result->H_nT) * (180.0 / M_PI);

    return 0;
}

int main(void) {
    GeodeticCoord kiev = {
        .latitude_deg = 50.4501,
        .longitude_deg = 30.5234,
        .altitude_km = 0.18,
        .epoch_year = 2025.0
    };

    IGRFCoefficients coeffs = { .epoch = 2025.0 };
    coeffs.g[1][0] = -29400.0;
    coeffs.g[1][1] = -1450.0;
    coeffs.h[1][1] = 4650.0;

    MagneticVector mag;
    if (igrf_calculate(&kiev, &coeffs, &mag) == 0) {
        printf("--- Геомагнітні компоненти у Києві (2025.0) ---\n");
        printf("Північна компонента (X):  %.1f нТл\n", mag.X_nT);
        printf("Східна компонента (Y):    %.1f нТл\n", mag.Y_nT);
        printf("Вертикальна компонента(Z):%.1f нТл\n", mag.Z_nT);
        printf("Горизонтальна напруга(H): %.1f нТл\n", mag.H_nT);
        printf("Повна індукція (F):       %.1f нТл\n", mag.F_nT);
        printf("Магнітна деклінація (D):  %.2f°\n", mag.D_deg);
        printf("Магнітна інклінація (I):  %.2f°\n", mag.I_deg);
    }
    return 0;
}
