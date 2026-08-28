#include <stdint.h>

/**
 * @brief Обчислення коду регістра DTG для таймера STM32
 * @param dead_time_ns Бажаний мертвий час у наносекундах
 * @param timer_freq_hz Частота тактування таймера (наприклад, 168000000 для 168 МГц)
 * @return 8-бітне значення для запису в поле TIM_BDTR_DTG
 */
uint8_t stm32_calc_deadtime_dtg(uint32_t dead_time_ns, uint32_t timer_freq_hz) {
    // Період одного такту таймера у наносекундах (з фіксованою точкою x1000)
    uint64_t t_dts_ps = 1000000000000ULL / timer_freq_hz;
    uint32_t ticks = (uint32_t)((dead_time_ns * 1000ULL + t_dts_ps / 2) / t_dts_ps);

    if (ticks <= 127) {
        // Діапазон 1: DTG[7]=0, крок = 1 такт
        return (uint8_t)ticks;
    } else if (ticks <= 254) {
        // Діапазон 2: DTG[7:6]=10, крок = 2 такти
        uint32_t raw = (ticks / 2) - 64;
        if (raw > 0x3F) raw = 0x3F;
        return (uint8_t)(0x80 | raw);
    } else if (ticks <= 504) {
        // Діапазон 3: DTG[7:5]=110, крок = 8 тактів
        uint32_t raw = (ticks / 8) - 32;
        if (raw > 0x1F) raw = 0x1F;
        return (uint8_t)(0xC0 | raw);
    } else if (ticks <= 1008) {
        // Діапазон 4: DTG[7:5]=111, крок = 16 тактів
        uint32_t raw = (ticks / 16) - 32;
        if (raw > 0x1F) raw = 0x1F;
        return (uint8_t)(0xE0 | raw);
    }

    // Перевищення максимального діапазону: встановлюємо абсолютний максимум
    return 0xFF;
}
