#ifndef RVDT_DRIVER_H
#define RVDT_DRIVER_H

#include <stdint.h>
#include <stdbool.h>

typedef enum {
    RVDT_STATUS_OK = 0,
    RVDT_STATUS_OPEN_CIRCUIT = 1,
    RVDT_STATUS_SHORT_CIRCUIT = 2,
    RVDT_STATUS_EXC_FAULT = 3
} rvdt_status_t;

typedef struct {
    float sensitivity_deg_per_ratio; // Чутливість (градуси на одиницю ратіо)
    float zero_offset_ratio;         // Зсув нульової точки
    float min_sum_voltage;           // Порогова мінімальна сума (V1 + V2)
    float max_sum_voltage;           // Порогова максимальна сума (V1 + V2)
    float lpf_alpha;                 // Коефіцієнт згладжування ФНЧ
} rvdt_config_t;

typedef struct {
    float v1_filtered;
    float v2_filtered;
    float ratiometric_value;
    float angle_degrees;
    rvdt_status_t status;
} rvdt_data_t;

void rvdt_init(const rvdt_config_t *cfg, rvdt_data_t *data);
rvdt_status_t rvdt_process_samples(const rvdt_config_t *cfg, rvdt_data_t *data, float raw_v1, float raw_v2);

#endif // RVDT_DRIVER_H
