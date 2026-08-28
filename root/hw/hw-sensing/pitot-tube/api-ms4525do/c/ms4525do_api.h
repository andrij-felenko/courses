// ms4525do_api.h — C-контракт драйвера MS4525DO
#ifndef MS4525DO_API_H
#define MS4525DO_API_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    MS4525_STATUS_OK           = 0,
    MS4525_STATUS_COMMAND_MODE = 1,
    MS4525_STATUS_STALE_DATA   = 2,
    MS4525_STATUS_FAULT        = 3,
    MS4525_STATUS_I2C_ERROR    = 4
} ms4525_status_t;

typedef struct {
    uint8_t i2c_address;     // Базова адреса 0x28
    float p_min_pa;          // -6894.76f для ±1 psi
    float p_max_pa;          // +6894.76f для ±1 psi
    float offset_pa;         // Зсув нуля, калібрований на землі
    int (*i2c_read)(uint8_t addr, uint8_t *buf, uint16_t len, void *ctx);
    void *user_ctx;
} ms4525_config_t;

typedef struct {
    float diff_pressure_pa;  // Виправлений диференціальний тиск
    float temperature_c;     // Температура кристала (°C)
    ms4525_status_t status;  // Статус пакету
    bool is_updated;         // Прапорець свіжих даних
} ms4525_sample_t;

void ms4525_init(ms4525_config_t *cfg);
ms4525_status_t ms4525_read_sample(const ms4525_config_t *cfg, ms4525_sample_t *out_sample);
ms4525_status_t ms4525_calibrate_zero(const ms4525_config_t *cfg, float *out_offset, uint16_t samples_count);

#ifdef __cplusplus
}
#endif

#endif // MS4525DO_API_H
