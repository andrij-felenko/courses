// Формування маски конфігурації INA219 мовою C (ESP-IDF / Bare-Metal)
#include <stdint.h>

#define INA219_REG_CONFIG       0x00

#define INA219_CONFIG_BRNG_32V  (1U << 13)
#define INA219_CONFIG_GAIN_80MV (1U << 11)  // PGA /2 (±80 мВ)
#define INA219_CONFIG_BADC_128X (0x0FU << 7) // 128x усереднення шини
#define INA219_CONFIG_SADC_128X (0x0FU << 3) // 128x усереднення шунта
#define INA219_CONFIG_MODE_CONT (0x07U << 0) // Безперервний режим Shunt + Bus

uint16_t ina219_make_config(void) {
    uint16_t config = INA219_CONFIG_BRNG_32V |
                      INA219_CONFIG_GAIN_80MV |
                      INA219_CONFIG_BADC_128X |
                      INA219_CONFIG_SADC_128X |
                      INA219_CONFIG_MODE_CONT;
    return config;
}
