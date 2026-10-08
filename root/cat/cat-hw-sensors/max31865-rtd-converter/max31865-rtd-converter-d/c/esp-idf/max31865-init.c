#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MAX31865_CONFIG_REG      0x00
#define MAX31865_RTD_MSB_REG     0x01
#define MAX31865_RTD_LSB_REG     0x02
#define MAX31865_FAULT_STAT_REG  0x07

#define MAX31865_CONFIG_VBIAS    (1 << 7)
#define MAX31865_CONFIG_AUTO     (1 << 6)
#define MAX31865_CONFIG_3WIRE    (1 << 4)
#define MAX31865_CONFIG_CLR_FLT  (1 << 1)
#define MAX31865_CONFIG_50HZ     (1 << 0)

#define RTD_A  3.9083e-3f
#define RTD_B -5.775e-7f

typedef struct {
    float r_ref;
    float r_0;
    bool is_3wire;
} max31865_config_t;

extern void spi_write_reg(uint8_t reg, uint8_t value);
extern void spi_read_regs(uint8_t start_reg, uint8_t *buffer, size_t len);

void max31865_init(const max31865_config_t *cfg) {
    uint8_t conf = MAX31865_CONFIG_VBIAS | MAX31865_CONFIG_AUTO | MAX31865_CONFIG_50HZ;
    if (cfg->is_3wire) {
        conf |= MAX31865_CONFIG_3WIRE;
    }
    conf |= MAX31865_CONFIG_CLR_FLT;
    spi_write_reg(MAX31865_CONFIG_REG | 0x80, conf);
}

bool max31865_read_temperature(const max31865_config_t *cfg, float *temperature_out) {
    uint8_t raw_bytes[2];
    spi_read_regs(MAX31865_RTD_MSB_REG, raw_bytes, 2);

    uint16_t raw_code = ((uint16_t)raw_bytes[0] << 8) | raw_bytes[1];
    if (raw_code & 0x0001) {
        return false;
    }

    uint16_t adc_code = raw_code >> 1;
    float r_rtd = ((float)adc_code * cfg->r_ref) / 32768.0f;

    float r_ratio = r_rtd / cfg->r_0;
    float discriminant = (RTD_A * RTD_A) - (4.0f * RTD_B * (1.0f - r_ratio));

    if (discriminant < 0.0f) {
        return false;
    }

    float temp = (-RTD_A + sqrtf(discriminant)) / (2.0f * RTD_B);

    if (temp < 0.0f) {
        float r_norm = (r_rtd / cfg->r_0) * 100.0f;
        temp = -242.02f + (2.2228f * r_norm) + (2.5859e-3f * r_norm * r_norm)
               - (4.8260e-6f * r_norm * r_norm * r_norm);
    }

    *temperature_out = temp;
    return true;
}
