#include <stdio.h>
#include <stdlib.h>

/* Імітація заголовка бібліотеки */
#include "superposition_engine.h"

int main(void) {
    /* 1. Налаштування точкових джерел полів */
    FieldSourceSpec sources[2] = {
        { .x = -1.0, .y = 0.0, .z = 0.0, .intensity = 1e-6, .phase_shift = 0.0 },
        { .x =  1.0, .y = 0.0, .z = 0.0, .intensity = 2e-6, .phase_shift = 0.0 }
    };

    TargetPointSpec target = { .x = 0.0, .y = 2.0, .z = 0.0 };
    FieldValueResult result;

    SupStatus status = SupEngine_CalculateFieldMatrix(sources, 2, &target, 1, &result);
    if (status == SUP_SUCCESS) {
        printf("Польова суперпозиція успішна:\n");
        printf("  F_total = (%e, %e, %e) Н/Кл\n", result.Fx, result.Fy, result.Fz);
        printf("  V_total = %e В\n", result.potential);
    }

    /* 2. Налаштування та запуск часової згортки (функція Гріна) */
    double h[3] = { 1.0, 0.5, 0.2 };
    GreenKernelConfig g_config = {
        .h_kernel = h,
        .h_length = 3,
        .max_amp = 5.0,
        .sample_rate = 1000.0
    };

    double signal[4] = { 0.5, 1.0, 1.5, 0.0 };
    double output[6];

    status = SupEngine_ProcessGreenConvolution(&g_config, signal, 4, output, 6);
    if (status == SUP_SUCCESS || status == SUP_WARN_NONLINEAR_SATURATION) {
        printf("Часова суперпозиція (згортка) успішна:\n");
        for (size_t i = 0; i < 6; ++i) {
            printf("  y[%zu] = %.3f\n", i, output[i]);
        }
        if (status == SUP_WARN_NONLINEAR_SATURATION) {
            printf("УВАГА: Виявлено насичення сигналу!\n");
        }
    }

    return 0;
}
