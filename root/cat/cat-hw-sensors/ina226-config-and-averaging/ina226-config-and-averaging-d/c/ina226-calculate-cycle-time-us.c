// Обчислення тривалості вимірювального циклу INA226 у мікросекундах
#include <stdint.h>
#include <stdbool.h>

// Таблиці тривалостей конверсії АЦП у мікросекундах та кількості усереднень
static const uint16_t CONV_TIME_US[] = {140, 204, 332, 588, 1101, 2116, 4156, 8244};
static const uint16_t AVG_SAMPLES[]  = {1, 4, 16, 64, 128, 256, 512, 1024};

uint32_t ina226_calculate_cycle_time_us(uint16_t config_reg) {
    uint8_t avg_idx  = (config_reg >> 9) & 0x07;
    uint8_t vbus_idx = (config_reg >> 6) & 0x07;
    uint8_t vsh_idx  = (config_reg >> 3) & 0x07;
    uint8_t mode     = config_reg & 0x07;

    uint32_t t_vsh  = (mode & 0x01) ? CONV_TIME_US[vsh_idx] : 0;
    uint32_t t_vbus = (mode & 0x02) ? CONV_TIME_US[vbus_idx] : 0;

    return (t_vsh + t_vbus) * AVG_SAMPLES[avg_idx];
}
