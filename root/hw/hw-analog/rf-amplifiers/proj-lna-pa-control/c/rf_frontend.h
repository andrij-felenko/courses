/* rf_frontend.h — Драйвер ВЧ-переднього кінця мовою C */
#ifndef RF_FRONTEND_H
#define RF_FRONTEND_H

#include <stdint.h>
#include <stdbool.h>

typedef enum {
    RF_MODE_SHUTDOWN = 0,
    RF_MODE_RX_HIGH_GAIN,
    RF_MODE_RX_BYPASS,
    RF_MODE_TX
} rf_mode_t;

typedef enum {
    RF_OK = 0,
    RF_ERR_INVALID_MODE,
    RF_ERR_OVERTEMP,
    RF_ERR_HIGH_VSWR,
    RF_ERR_NULL_PTR
} rf_status_t;

typedef struct {
    float temp_celsius;
    float forward_power_dbm;
    float reverse_power_dbm;
    float vswr;
} rf_telemetry_t;

/* Конфігураційні межі захисту */
#define RF_MAX_TEMP_C      85.0f
#define RF_MAX_VSWR        3.0f

void rf_frontend_init(void);
rf_status_t rf_frontend_set_mode(rf_mode_t new_mode);
rf_mode_t rf_frontend_get_mode(void);
rf_status_t rf_frontend_read_telemetry(rf_telemetry_t *telemetry);

#endif /* RF_FRONTEND_H */
