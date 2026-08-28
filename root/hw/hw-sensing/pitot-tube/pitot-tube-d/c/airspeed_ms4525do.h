// airspeed_ms4525do.h — C-драйвер цифрового вимірювача швидкості потоку
#ifndef AIRSPEED_MS4525DO_H
#define AIRSPEED_MS4525DO_H

#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MS4525DO_I2C_ADDR         0x28
#define MS4525DO_PSI_SPAN         1.0f        // Діапазон ±1 psi
#define PSI_TO_PASCALS            6894.757f
#define AIR_DENSITY_SEA_LEVEL     1.2250f     // Стандартна густина ρ₀ (кг/м³)
#define AIR_GAS_CONSTANT          287.058f    // Дж / (кг · К)

typedef enum {
    AIRSPEED_OK = 0,
    AIRSPEED_STALE_DATA,
    AIRSPEED_SENSOR_FAULT,
    AIRSPEED_BUS_ERROR,
    AIRSPEED_CALIBRATING
} airspeed_status_t;

typedef struct {
    float ias_mps;             // Приладова швидкість (м/с)
    float tas_mps;             // Істинна швидкість з поправкою на густину (м/с)
    float diff_pressure_pa;    // Фільтрований динамічний перепад тиску (Па)
    float raw_pressure_pa;     // Миттєвий перепад тиску без фільтрації (Па)
    float temperature_c;       // Температура кристала (°C)
    float air_density;         // Розрахована дійсна густина повітря (кг/м³)
    airspeed_status_t status;  // Стан вимірювання
} airspeed_data_t;

typedef struct {
    uint8_t i2c_addr;
    float zero_offset_pa;      // Калібрований зсув нуля (Па)
    float lpf_alpha;           // Коефіцієнт згладжування ФНЧ (0.0..1.0)
    float filtered_pa;         // Стан фільтра тиску
    bool is_calibrated;
    // Покажчик на платформову функцію I2C-читання:
    int (*i2c_read_fn)(uint8_t addr, uint8_t *data, uint16_t len, void *ctx);
    void *user_ctx;
} airspeed_sensor_t;

void airspeed_init(airspeed_sensor_t *dev, 
                   int (*read_fn)(uint8_t, uint8_t*, uint16_t, void*), 
                   void *user_ctx) {
    dev->i2c_addr = MS4525DO_I2C_ADDR;
    dev->zero_offset_pa = 0.0f;
    dev->lpf_alpha = 0.20f;     // Постійна часу фільтрації
    dev->filtered_pa = 0.0f;
    dev->is_calibrated = false;
    dev->i2c_read_fn = read_fn;
    dev->user_ctx = user_ctx;
}

airspeed_status_t airspeed_calibrate_zero(airspeed_sensor_t *dev, uint16_t samples) {
    if (!dev->i2c_read_fn || samples == 0) return AIRSPEED_BUS_ERROR;
    
    float accum_pa = 0.0f;
    uint16_t valid_samples = 0;
    uint8_t buf[4];

    for (uint16_t i = 0; i < samples; i++) {
        if (dev->i2c_read_fn(dev->i2c_addr, buf, 4, dev->user_ctx) == 0) {
            uint8_t status_bits = (buf[0] >> 6) & 0x03;
            if (status_bits == 0x00 || status_bits == 0x02) {
                uint16_t raw_p = (((uint16_t)(buf[0] & 0x3F)) << 8) | buf[1];
                // Перерахунок у Паскалі для Type A (10%..90% розмах)
                float p_psi = (((float)raw_p - 1638.0f) * (2.0f * MS4525DO_PSI_SPAN) / 13107.0f) - MS4525DO_PSI_SPAN;
                accum_pa += (p_psi * PSI_TO_PASCALS);
                valid_samples++;
            }
        }
    }

    if (valid_samples < (samples / 2)) {
        return AIRSPEED_SENSOR_FAULT;
    }

    dev->zero_offset_pa = accum_pa / (float)valid_samples;
    dev->filtered_pa = 0.0f;
    dev->is_calibrated = true;
    return AIRSPEED_OK;
}

airspeed_status_t airspeed_update(airspeed_sensor_t *dev, 
                                  float baro_pressure_pa, 
                                  float ambient_temp_c, 
                                  airspeed_data_t *out) {
    if (!dev->i2c_read_fn) return AIRSPEED_BUS_ERROR;

    uint8_t buf[4];
    int err = dev->i2c_read_fn(dev->i2c_addr, buf, 4, dev->user_ctx);
    if (err != 0) {
        out->status = AIRSPEED_BUS_ERROR;
        return AIRSPEED_BUS_ERROR;
    }

    uint8_t status_bits = (buf[0] >> 6) & 0x03;
    if (status_bits == 0x03) {
        out->status = AIRSPEED_SENSOR_FAULT;
        return AIRSPEED_SENSOR_FAULT;
    }
    if (status_bits == 0x02) {
        out->status = AIRSPEED_STALE_DATA;
        return AIRSPEED_STALE_DATA;
    }

    // 1. Розпакування сирих кодів АЦП
    uint16_t raw_press = (((uint16_t)(buf[0] & 0x3F)) << 8) | buf[1];
    uint16_t raw_temp  = (((uint16_t)buf[2]) << 3) | (buf[3] >> 5);

    // 2. Розрахунок тиску та температури
    float p_psi = (((float)raw_press - 1638.0f) * (2.0f * MS4525DO_PSI_SPAN) / 13107.0f) - MS4525DO_PSI_SPAN;
    float p_pa = (p_psi * PSI_TO_PASCALS) - dev->zero_offset_pa;
    out->raw_pressure_pa = p_pa;
    out->temperature_c = (((float)raw_temp * 200.0f) / 2047.0f) - 50.0f;

    // 3. Захист від від'ємного перепаду тиску
    float clean_p = (p_pa < 0.0f) ? 0.0f : p_pa;

    // 4. Експоненційний фільтр низьких частот (EMA)
    dev->filtered_pa = dev->filtered_pa + dev->lpf_alpha * (clean_p - dev->filtered_pa);
    out->diff_pressure_pa = dev->filtered_pa;

    // 5. Розрахунок приладової швидкості (IAS) за стандартною густиною
    out->ias_mps = sqrtf((2.0f * out->diff_pressure_pa) / AIR_DENSITY_SEA_LEVEL);

    // 6. Розрахунок дійсної густини та істинної швидкості (TAS)
    float baro = (baro_pressure_pa > 30000.0f) ? baro_pressure_pa : 101325.0f;
    float temp_k = (ambient_temp_c > -100.0f) ? (ambient_temp_c + 273.15f) : (out->temperature_c + 273.15f);
    out->air_density = baro / (AIR_GAS_CONSTANT * temp_k);
    
    if (out->air_density > 0.1f) {
        out->tas_mps = sqrtf((2.0f * out->diff_pressure_pa) / out->air_density);
    } else {
        out->tas_mps = out->ias_mps;
    }

    out->status = AIRSPEED_OK;
    return AIRSPEED_OK;
}
#endif // AIRSPEED_MS4525DO_H
