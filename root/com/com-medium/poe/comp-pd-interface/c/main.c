#include <stdint.h>
#include <stdbool.h>

/* Статуси детекції порту PSE за стандартом IEEE 802.3 */
typedef enum {
    POE_DET_UNKNOWN     = 0,
    POE_DET_VALID_25K   = 1, /* Виявлено валідну сигнатуру 24.9 кОм */
    POE_DET_LOW_RES     = 2, /* Занижений опір (коротке замикання) */
    POE_DET_HIGH_RES    = 3, /* Завищений опір або відкрита лінія */
    POE_DET_HIGH_CAP    = 4  /* Ємність лінії > 150 нФ */
} poe_detection_status_t;

/* Сирі дані телеметрії порта з регістрів контролера */
typedef struct {
    uint16_t voltage_raw_mv;   /* Напруга в мілівольтах (наприклад 54000) */
    uint16_t current_raw_ma;   /* Струм у міліамперах */
    uint8_t  detection_code;   /* Код регістру детекції */
    uint8_t  fault_flags;      /* Біти аварій: bit0=OCP, bit1=UVLO, bit2=OTP */
} poe_port_raw_telemetry_t;

/* Обчислений діагностичний звіт */
typedef struct {
    float voltage_v;
    float current_a;
    float power_w;
    poe_detection_status_t status;
    bool is_powered;
    bool has_fault;
} poe_port_metrics_t;

bool poe_parse_telemetry(const poe_port_raw_telemetry_t *raw, poe_port_metrics_t *out) {
    if (!raw || !out) {
        return false;
    }

    out->voltage_v = (float)raw->voltage_raw_mv / 1000.0f;
    out->current_a = (float)raw->current_raw_ma / 1000.0f;
    out->power_w   = out->voltage_v * out->current_a;

    switch (raw->detection_code) {
        case 0x01: out->status = POE_DET_VALID_25K; break;
        case 0x02: out->status = POE_DET_LOW_RES;   break;
        case 0x03: out->status = POE_DET_HIGH_RES;  break;
        case 0x04: out->status = POE_DET_HIGH_CAP;  break;
        default:   out->status = POE_DET_UNKNOWN;   break;
    }

    out->is_powered = (raw->voltage_raw_mv >= 44000);
    out->has_fault  = (raw->fault_flags != 0);

    return true;
}
