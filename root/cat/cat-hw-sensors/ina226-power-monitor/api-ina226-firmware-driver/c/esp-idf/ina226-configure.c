#include <stdint.h>
#include <stdbool.h>

#define INA226_REG_CONFIG 0x00
#define INA226_CFG_RESET  0x8000

typedef enum {
    INA226_AVG_1    = 0x0000,
    INA226_AVG_16   = 0x0400,
    INA226_AVG_64   = 0x0600,
    INA226_AVG_128  = 0x0800,
    INA226_AVG_1024 = 0x0E00
} ina226_avg_t;

typedef enum {
    INA226_CT_1100US = 0x0020,
    INA226_CT_2116US = 0x0028,
    INA226_CT_8244US = 0x0038
} ina226_ct_t;

typedef enum {
    INA226_MODE_POWER_DOWN = 0x0000,
    INA226_MODE_TRIG_SH_BUS= 0x0003,
    INA226_MODE_CONT_SH_BUS= 0x0007
} ina226_mode_t;

bool ina226_configure(ina226_avg_t avg, ina226_ct_t vbus_ct, ina226_ct_t vsh_ct, ina226_mode_t mode) {
    uint16_t config_val = 0x4000 | (uint16_t)avg | ((uint16_t)vbus_ct << 3) | (uint16_t)vsh_ct | (uint16_t)mode;
    return hal_i2c_write_reg16(INA226_REG_CONFIG, config_val);
}
