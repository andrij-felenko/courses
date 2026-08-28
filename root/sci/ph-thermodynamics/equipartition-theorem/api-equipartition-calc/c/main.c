#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define K_BOLTZMANN 1.380649e-23
#define K_AVOGADRO 6.02214076e23
#define K_GAS_CONSTANT (K_BOLTZMANN * K_AVOGADRO)

typedef struct {
    int degrees_trans;
    int degrees_rot;
    size_t num_vib_modes;
    const double* vib_temperatures;
    double rot_temperature;
} MoleculeConfigC;

double classical_molar_heat_capacity_cv_c(const MoleculeConfigC* config) {
    double f_total_quad = (double)config->degrees_trans + (double)config->degrees_rot + 2.0 * (double)config->num_vib_modes;
    return 0.5 * f_total_quad * K_GAS_CONSTANT;
}

double quantum_molar_heat_capacity_cv_c(const MoleculeConfigC* config, double temp_kelvin) {
    if (temp_kelvin <= 0.0) return -1.0;

    double cv_sum = 0.5 * (double)config->degrees_trans * K_GAS_CONSTANT;

    if (config->degrees_rot > 0) {
        if (temp_kelvin > config->rot_temperature) {
            cv_sum += 0.5 * (double)config->degrees_rot * K_GAS_CONSTANT;
        } else {
            double ratio = config->rot_temperature / temp_kelvin;
            cv_sum += 0.5 * (double)config->degrees_rot * K_GAS_CONSTANT * exp(-ratio);
        }
    }

    for (size_t i = 0; i < config->num_vib_modes; ++i) {
        double x = config->vib_temperatures[i] / temp_kelvin;
        if (x > 100.0) continue;
        double exp_x = exp(x);
        double einstein_factor = (x * x * exp_x) / ((exp_x - 1.0) * (exp_x - 1.0));
        cv_sum += K_GAS_CONSTANT * einstein_factor;
    }

    return cv_sum;
}

int main(void) {
    double n2_vib_temps[1] = {3371.0};
    MoleculeConfigC n2_cfg = {
        .degrees_trans = 3,
        .degrees_rot = 2,
        .num_vib_modes = 1,
        .vib_temperatures = n2_vib_temps,
        .rot_temperature = 2.88
    };

    printf("Класична C_V (C): %.2f Дж/(моль·К)\n", classical_molar_heat_capacity_cv_c(&n2_cfg));
    printf("Квантова C_V при 300K (C): %.2f Дж/(моль·К)\n", quantum_molar_heat_capacity_cv_c(&n2_cfg, 300.0));

    return 0;
}
