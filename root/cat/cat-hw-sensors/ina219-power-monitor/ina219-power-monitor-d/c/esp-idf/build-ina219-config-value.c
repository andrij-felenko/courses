// Налаштування регістру Configuration для INA219: FSR = 32V, PGA = /2 (+-80mV), 128x OSR, Continuous
#include <stdint.h>

#define INA219_REG_CONFIG       0x00

#define INA219_CONFIG_BRNG_32V  (1 << 13)
#define INA219_CONFIG_GAIN_80MV (1 << 11)   // PG1=0, PG0=1 (+-80mV)
#define INA219_CONFIG_BADC_128X (0x0F << 7) // 128 вибірок для Bus ADC
#define INA219_CONFIG_SADC_128X (0x0F << 3) // 128 вибірок для Shunt ADC
#define INA219_CONFIG_MODE_CONT (0x07 << 0) // Shunt + Bus Continuous mode

uint16_t build_ina219_config_value(void) {
    // Формування 16-бітного значення конфігураційного регістра
    uint16_t config = INA219_CONFIG_BRNG_32V |
                      INA219_CONFIG_GAIN_80MV |
                      INA219_CONFIG_BADC_128X |
                      INA219_CONFIG_SADC_128X |
                      INA219_CONFIG_MODE_CONT;
    return config;
}
