/* esm3000_api.h - C API драйвера електростатичного флюксметра ESM-3000 */
#ifndef ESM3000_API_H
#define ESM3000_API_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    ESM_RANGE_1KV   = 0x00, /* Діапазон ±1 кВ/м  (Крок LSB = 0.0305 В/м) */
    ESM_RANGE_5KV   = 0x01, /* Діапазон ±5 кВ/м  (Крок LSB = 0.1525 В/м) */
    ESM_RANGE_20KV  = 0x02, /* Діапазон ±20 кВ/м (Крок LSB = 0.6103 В/м) */
    ESM_RANGE_100KV = 0x03  /* Діапазон ±100 кВ/м(Крок LSB = 3.0517 В/м) */
} esm_range_t;

typedef struct {
    uint8_t i2c_address;
    esm_range_t range;
    float alarm_threshold_kv_m;
    bool enable_interrupt;
} esm_config_t;

typedef struct {
    float field_kv_m;          /* Напруженість поля у кВ/м з врахуванням знака */
    float induced_charge_nC;   /* Обчислений індукований заряд на сенсорі (нКл) */
    bool alarm_active;         /* Прапорець апаратної тривоги ESD */
    bool sensor_saturated;     /* Прапорець переповнення вимірювального тракту */
} esm_measurement_t;

/* Функції низькорівневого та високорівневого керування */
int esm_init(const esm_config_t* config);
int esm_read_measurement(esm_measurement_t* result);
int esm_set_calibration_zero(int16_t offset_raw);
int esm_soft_reset(void);

#ifdef __cplusplus
}
#endif

#endif /* ESM3000_API_H */
