#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define SPEED_OF_LIGHT 299792458.0
#define PI 3.14159265358979323846
#define MU_0 (4.0 * PI * 1e-7)

// Питома електропровідність матеріалів (См/м)
#define SIGMA_COPPER 5.8e7
#define SIGMA_ALUMINUM 3.5e7

typedef enum {
    ANTENNA_DIPOLE,
    ANTENNA_MONOPOLE,
    ANTENNA_LOOP
} AntennaType;

typedef struct {
    AntennaType type;
    double length_m;        // Довжина диполя/монополя або периметр рамки (м)
    double wire_radius_m;   // Радіус дроту (м)
    double conductivity;    // Питома провідність σ (См/м)
    int loop_turns;         // Кількість витків (для рамкової антени)
} AntennaParams;

typedef struct {
    double wavelength_m;
    double skin_depth_m;
    double r_rad_ohm;
    double r_loss_ohm;
    double efficiency_linear;
    double efficiency_db;
} AntennaResult;

bool calculate_antenna_performance(double freq_hz, const AntennaParams *params, AntennaResult *result) {
    if (freq_hz <= 0.0 || params->length_m <= 0.0 || params->wire_radius_m <= 0.0) {
        return false;
    }

    double lambda = SPEED_OF_LIGHT / freq_hz;
    result->wavelength_m = lambda;

    // Глибина скін-шару δ
    double delta = 1.0 / sqrt(PI * freq_hz * MU_0 * params->conductivity);
    result->skin_depth_m = delta;

    double l_rel = params->length_m / lambda;
    double r_rad = 0.0;

    switch (params->type) {
        case ANTENNA_DIPOLE:
            if (l_rel < 0.1) {
                // Короткий диполь з лінійним розподілом струму
                r_rad = 20.0 * PI * PI * l_rel * l_rel;
            } else if (fabs(l_rel - 0.5) < 0.05) {
                // Півхвильовий диполь
                r_rad = 73.13;
            } else {
                // Загальна напівімпірична апроксимація
                r_rad = 20.0 * PI * PI * l_rel * l_rel * (1.0 + 0.3 * l_rel);
            }
            break;

        case ANTENNA_MONOPOLE:
            // Монополь над ідеальним екраном має удвічі менший R_rad
            if (l_rel < 0.05) {
                r_rad = 10.0 * PI * PI * (4.0 * l_rel * l_rel);
            } else if (fabs(l_rel - 0.25) < 0.025) {
                r_rad = 36.56;
            } else {
                r_rad = 10.0 * PI * PI * (4.0 * l_rel * l_rel);
            }
            break;

        case ANTENNA_LOOP: {
            // Мала рамкова антена радіусом R_loop
            double r_loop = params->length_m / (2.0 * PI);
            double area = PI * r_loop * r_loop;
            double n = (double)params->loop_turns;
            r_rad = 31200.0 * n * n * (area * area) / (lambda * lambda * lambda * lambda);
            break;
        }
    }

    // Високочастотний опір дрітного провідника
    double r_loss = params->length_m / (2.0 * PI * params->wire_radius_m * params->conductivity * delta);

    result->r_rad_ohm = r_rad;
    result->r_loss_ohm = r_loss;

    double eff = r_rad / (r_rad + r_loss);
    result->efficiency_linear = eff;
    result->efficiency_db = 10.0 * log10(eff);

    return true;
}

int main(void) {
    double freq = 144.0e6; // 144 МГц (радіоаматорський діапазон 2м)

    AntennaParams dipole_params = {
        .type = ANTENNA_DIPOLE,
        .length_m = 1.02,           // ~ 0.49 λ (резонансний півхвильовий диполь)
        .wire_radius_m = 0.001,      // 1 мм мідна жила
        .conductivity = SIGMA_COPPER,
        .loop_turns = 1
    };

    AntennaResult res;
    if (calculate_antenna_performance(freq, &dipole_params, &res)) {
        printf("=== Аналіз дипольної антени (f = %.1f МГц) ===\n", freq / 1e6);
        printf("Довжина хвилі λ:    %.3f м\n", res.wavelength_m);
        printf("Скін-шар δ:         %.2f мкм\n", res.skin_depth_m * 1e6);
        printf("Опір випромінювання R_рад: %.2f Ом\n", res.r_rad_ohm);
        printf("Опір втрат R_втрат:        %.4f Ом\n", res.r_loss_ohm);
        printf("ККД антени η:              %.2f%% (%.2f дБ)\n",
               res.efficiency_linear * 100.0, res.efficiency_db);
    }
    return 0;
}
