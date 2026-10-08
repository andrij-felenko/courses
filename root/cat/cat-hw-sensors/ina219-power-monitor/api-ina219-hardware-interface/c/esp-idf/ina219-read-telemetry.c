// Зчитування телеметрії INA219 з обробкою прапорців CNVR та OVF для ESP-IDF
#include <stdint.h>
#include <stdbool.h>

#define INA219_REG_BUS_VOLTAGE  0x02
#define INA219_REG_CURRENT      0x04
#define INA219_REG_POWER        0x03

#define INA219_BUS_CNVR_MASK    (1 << 1)
#define INA219_BUS_OVF_MASK     (1 << 0)

typedef struct {
    float bus_voltage_v;
    float current_ma;
    float power_mw;
    bool data_ready;
    bool overflow;
} ina219_telemetry_t;

// Функція обробки даних (імітація I2C читання 16-бітних регістрів)
bool ina219_read_telemetry(uint16_t reg_bus, int16_t reg_current, uint16_t reg_power, 
                          float current_lsb_ma, ina219_telemetry_t *out_data) 
{
    out_data->data_ready = (reg_bus & INA219_BUS_CNVR_MASK) != 0;
    out_data->overflow = (reg_bus & INA219_BUS_OVF_MASK) != 0;

    if (out_data->overflow) {
        // При переповненні дані струму та потужності недостовірні
        out_data->current_ma = 0.0f;
        out_data->power_mw = 0.0f;
        return false;
    }

    // Декодування напруги шини (біти 15..3, LSB = 4 мВ = 0.004 В)
    uint16_t raw_bus = reg_bus >> 3;
    out_data->bus_voltage_v = raw_bus * 0.004f;

    // Декодування струму та потужності
    out_data->current_ma = reg_current * current_lsb_ma;
    out_data->power_mw = reg_power * 20.0f * current_lsb_ma;

    return true;
}
