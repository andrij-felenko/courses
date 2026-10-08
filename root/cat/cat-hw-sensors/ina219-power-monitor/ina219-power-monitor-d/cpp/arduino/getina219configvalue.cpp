// Налаштування регістру Configuration для INA219: FSR = 32V, PGA = /2 (+-80mV), 128x OSR, Continuous
#include <Arduino.h>

constexpr uint8_t INA219_REG_CONFIG = 0x00;

constexpr uint16_t INA219_CONFIG_BRNG_32V  = (1U << 13);
constexpr uint16_t INA219_CONFIG_GAIN_80MV = (1U << 11);   // PG1=0, PG0=1 (+-80mV)
constexpr uint16_t INA219_CONFIG_BADC_128X = (0x0FU << 7); // 128 вибірок для Bus ADC
constexpr uint16_t INA219_CONFIG_SADC_128X = (0x0FU << 3); // 128 вибірок для Shunt ADC
constexpr uint16_t INA219_CONFIG_MODE_CONT = (0x07U << 0); // Shunt + Bus Continuous mode

uint16_t getIna219ConfigValue() {
    // Формування 16-бітного значення конфігураційного регістра
    uint16_t config = INA219_CONFIG_BRNG_32V |
                      INA219_CONFIG_GAIN_80MV |
                      INA219_CONFIG_BADC_128X |
                      INA219_CONFIG_SADC_128X |
                      INA219_CONFIG_MODE_CONT;
    return config;
}
