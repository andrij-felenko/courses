#include <stdint.h>
#include <stdbool.h>

#define INA226_ADDR         0x40
#define REG_CONFIG          0x00
#define REG_CURRENT         0x04
#define REG_BUS_VOLTAGE     0x02
#define REG_CALIBRATION     0x05

typedef struct {
    uint16_t current_limit_ma;
    uint16_t max_voltage_mv;
    bool is_armed;
} PowerProtection_t;

bool check_power_rails(PowerProtection_t *prot, int16_t raw_current, uint16_t raw_voltage) {
    /* 200 мкА на розряд струму, 1.25 мВ на розряд напруги */
    int32_t current_ma = ((int32_t)raw_current * 200) / 1000;
    uint32_t voltage_mv = ((uint32_t)raw_voltage * 1250) / 1000;

    if (!prot->is_armed) {
        return true;
    }

    if (current_ma > prot->current_limit_ma || voltage_mv > prot->max_voltage_mv) {
        prot->is_armed = false; /* Аварійне вимкнення */
        return false;
    }

    return true;
}
