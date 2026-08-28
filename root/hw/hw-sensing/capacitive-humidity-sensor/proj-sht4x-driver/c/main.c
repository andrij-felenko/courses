#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define SHT4X_I2C_ADDR_DEFAULT  0x44

typedef enum {
    SHT4X_CMD_MEASURE_HIGH_PREC     = 0xFD,
    SHT4X_CMD_MEASURE_MED_PREC      = 0xF6,
    SHT4X_CMD_MEASURE_LOW_PREC      = 0xE0,
    SHT4X_CMD_READ_SERIAL           = 0x89,
    SHT4X_CMD_SOFT_RESET            = 0x94,
    SHT4X_CMD_HEATER_200MW_1SEC     = 0x39,
    SHT4X_CMD_HEATER_200MW_0P1SEC   = 0x32,
    SHT4X_CMD_HEATER_110MW_1SEC     = 0x2F,
    SHT4X_CMD_HEATER_110MW_0P1SEC   = 0x24,
    SHT4X_CMD_HEATER_20MW_1SEC      = 0x1E,
    SHT4X_CMD_HEATER_20MW_0P1SEC    = 0x15
} sht4x_command_t;

typedef enum {
    SHT4X_OK = 0,
    SHT4X_ERR_I2C = -1,
    SHT4X_ERR_CRC_TEMP = -2,
    SHT4X_ERR_CRC_RH = -3,
    SHT4X_ERR_PARAM = -4
} sht4x_status_t;

typedef struct {
    float temperature_c;     // Температура повітря, °C
    float relative_humidity; // Відносна вологість, % RH (0.0 .. 100.0)
    float dew_point_c;       // Точка роси, °C
    float absolute_hum_gm3;  // Абсолютна вологість, г/м³
} sht4x_data_t;

// Інтерфейс апаратного рівня (Hardware Abstraction Layer)
typedef struct {
    int (*i2c_write)(uint8_t addr, const uint8_t *data, uint16_t len);
    int (*i2c_read)(uint8_t addr, uint8_t *data, uint16_t len);
    void (*delay_ms)(uint32_t ms);
} sht4x_hal_t;

// Обчислення CRC-8 (поліном 0x31, ініціалізація 0xFF)
static uint8_t sht4x_crc8(const uint8_t *data, uint16_t len) {
    uint8_t crc = 0xFF;
    for (uint16_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x80) {
                crc = (uint8_t)((crc << 1) ^ 0x31);
            } else {
                crc = (uint8_t)(crc << 1);
            }
        }
    }
    return crc;
}

// Розрахунок точки роси та абсолютної вологості за формулою Магнуса
static void sht4x_compute_psychrometrics(sht4x_data_t *res) {
    const float b = 17.62f;
    const float c = 243.12f;
    
    float rh_clamped = res->relative_humidity;
    if (rh_clamped < 0.1f) rh_clamped = 0.1f;
    if (rh_clamped > 100.0f) rh_clamped = 100.0f;
    
    float gamma = logf(rh_clamped / 100.0f) + (b * res->temperature_c) / (c + res->temperature_c);
    res->dew_point_c = (c * gamma) / (b - gamma);
    
    // Парціальний тиск водяної пари (гПа) та абсолютна вологість (г/м³)
    float p_sat = 6.112f * expf((b * res->temperature_c) / (c + res->temperature_c));
    float p_actual = (rh_clamped / 100.0f) * p_sat;
    res->absolute_hum_gm3 = 216.7f * p_actual / (res->temperature_c + 273.15f);
}

sht4x_status_t sht4x_read_sample(const sht4x_hal_t *hal, uint8_t addr, 
                                 sht4x_command_t cmd, sht4x_data_t *result) {
    if (!hal || !hal->i2c_write || !hal->i2c_read || !hal->delay_ms || !result) {
        return SHT4X_ERR_PARAM;
    }

    uint8_t cmd_byte = (uint8_t)cmd;
    if (hal->i2c_write(addr, &cmd_byte, 1) != 0) {
        return SHT4X_ERR_I2C;
    }

    // Затримка на вимірювання згідно зі специфікацією
    uint32_t delay_time = 10;
    if (cmd == SHT4X_CMD_MEASURE_LOW_PREC) delay_time = 2;
    else if (cmd == SHT4X_CMD_MEASURE_MED_PREC) delay_time = 5;
    else if (cmd == SHT4X_CMD_HEATER_200MW_1SEC || cmd == SHT4X_CMD_HEATER_110MW_1SEC || 
             cmd == SHT4X_CMD_HEATER_20MW_1SEC) delay_time = 1100;
    else if (cmd == SHT4X_CMD_HEATER_200MW_0P1SEC || cmd == SHT4X_CMD_HEATER_110MW_0P1SEC || 
             cmd == SHT4X_CMD_HEATER_20MW_0P1SEC) delay_time = 120;
    
    hal->delay_ms(delay_time);

    uint8_t buf[6];
    if (hal->i2c_read(addr, buf, 6) != 0) {
        return SHT4X_ERR_I2C;
    }

    // Перевірка контрольних сум для температури й вологості
    if (sht4x_crc8(&buf[0], 2) != buf[2]) {
        return SHT4X_ERR_CRC_TEMP;
    }
    if (sht4x_crc8(&buf[3], 2) != buf[5]) {
        return SHT4X_ERR_CRC_RH;
    }

    uint16_t raw_temp = ((uint16_t)buf[0] << 8) | buf[1];
    uint16_t raw_rh   = ((uint16_t)buf[3] << 8) | buf[4];

    result->temperature_c = -45.0f + 175.0f * ((float)raw_temp / 65535.0f);
    float rh = -6.0f + 125.0f * ((float)raw_rh / 65535.0f);
    if (rh < 0.0f) rh = 0.0f;
    if (rh > 100.0f) rh = 100.0f;
    result->relative_humidity = rh;

    sht4x_compute_psychrometrics(result);
    return SHT4X_OK;
}
