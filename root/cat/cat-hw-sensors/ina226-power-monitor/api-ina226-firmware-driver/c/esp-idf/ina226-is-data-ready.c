#include <stdint.h>
#include <stdbool.h>

#define INA226_REG_BUS_VOLTAGE   0x02
#define INA226_REG_CURRENT       0x04
#define INA226_REG_POWER         0x03
#define INA226_REG_MASK_ENABLE   0x06
#define INA226_BIT_CVRF          (1 << 3)

typedef struct {
    float bus_voltage_v;
    float current_a;
    float power_w;
} ina226_data_t;

bool ina226_is_data_ready(void) {
    uint16_t mask_reg = 0;
    if (!hal_i2c_read_reg16(INA226_REG_MASK_ENABLE, &mask_reg)) {
        return false;
    }
    return (mask_reg & INA226_BIT_CVRF) != 0;
}

bool ina226_read_telemetry(float current_lsb, ina226_data_t *data) {
    uint16_t raw_bus, raw_current, raw_power;
    if (!hal_i2c_read_reg16(INA226_REG_BUS_VOLTAGE, &raw_bus)) return false;
    if (!hal_i2c_read_reg16(INA226_REG_CURRENT, &raw_current)) return false;
    if (!hal_i2c_read_reg16(INA226_REG_POWER, &raw_power)) return false;

    data->bus_voltage_v = (int16_t)raw_bus * 0.00125f;
    data->current_a = (int16_t)raw_current * current_lsb;
    data->power_w = raw_power * (25.0f * current_lsb);
    return true;
}
