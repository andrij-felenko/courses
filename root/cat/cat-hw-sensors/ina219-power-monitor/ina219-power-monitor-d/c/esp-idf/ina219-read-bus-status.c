// Зчитування регістра 02h та обробка прапорців CNVR і OVF
#include <stdint.h>
#include <stdbool.h>

#define INA219_REG_BUS_VOLTAGE 0x02

typedef struct {
    uint16_t bus_voltage_raw;
    bool conversion_ready;
    bool math_overflow;
} ina219_bus_status_t;

bool ina219_read_bus_status(uint16_t reg_02h_value, ina219_bus_status_t *status) {
    if (!status) return false;
    
    // Старші 13 бітів (15..3) містять напругу шини (LSB = 4 мВ)
    status->bus_voltage_raw = reg_02h_value >> 3;
    
    // Біт 1: Conversion Ready (CNVR)
    status->conversion_ready = (reg_02h_value & (1 << 1)) != 0;
    
    // Біт 0: Math Overflow (OVF)
    status->math_overflow = (reg_02h_value & (1 << 0)) != 0;
    
    return true;
}
