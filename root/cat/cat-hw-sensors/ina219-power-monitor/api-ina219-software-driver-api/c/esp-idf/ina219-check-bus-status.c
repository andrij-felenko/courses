// Перевірка прапорців CNVR та OVF мовою C
#include <stdbool.h>
#include <stdint.h>

#define INA219_REG_BUS_VOLTAGE 0x02
#define INA219_BUS_CNVR_MASK   (1U << 1)
#define INA219_BUS_OVF_MASK    (1U << 0)

typedef struct {
    bool ready;
    bool overflow;
    float voltage;
} ina219_bus_status_t;

ina219_bus_status_t ina219_check_bus_status(uint16_t raw_bus_reg) {
    ina219_bus_status_t status;
    status.ready = (raw_bus_reg & INA219_BUS_CNVR_MASK) != 0;
    status.overflow = (raw_bus_reg & INA219_BUS_OVF_MASK) != 0;
    status.voltage = (float)(raw_bus_reg >> 3) * 0.004f;
    return status;
}
