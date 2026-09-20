#include <stdio.h>
#include "rvdt_driver.h"

int main(void) {
    printf("=== Драйвер обробки сигналів RVDT (Ратіометричне обчислення кута) ===\n");

    rvdt_config_t config = {
        .sensitivity_deg_per_ratio = 60.0f,
        .zero_offset_ratio = 0.0f,
        .min_sum_voltage = 1.0f,
        .max_sum_voltage = 5.5f,
        .lpf_alpha = 0.3f
    };

    rvdt_data_t rvdt_data;
    rvdt_init(&config, &rvdt_data);

    float raw_samples[][2] = {
        { 2.50f, 2.50f },
        { 3.125f, 1.875f },
        { 3.75f, 1.25f },
        { 0.10f, 0.05f }
    };

    for (int i = 0; i < 4; ++i) {
        rvdt_status_t status = rvdt_process_samples(&config, &rvdt_data, raw_samples[i][0], raw_samples[i][1]);

        printf("Крок %d: V1=%.2fV V2=%.2fV -> Ratio=%.3f, Кут=%.2f град. (Статус=%d)\n",
               i, raw_samples[i][0], raw_samples[i][1],
               rvdt_data.ratiometric_value, rvdt_data.angle_degrees, status);
    }

    return 0;
}
