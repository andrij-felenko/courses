#include <stdint.h>

// Стан LFSR на k-му кроці від зерна — перемотка з нуля.
// Дорого при великих k, але завжди дає ТОЧНО той самий стан на обох кінцях.
static uint16_t lfsr16_at(uint16_t seed, uint32_t k) {
    uint16_t s = lfsr16_seed(seed);
    for (uint32_t i = 0; i < k; i++)
        s = lfsr16_step(s);
    return s;
}

// Канал для кадру номер frame — обидва кінці рахують те саме число.
uint8_t channel_for_frame(uint16_t seed, uint32_t frame, uint8_t prev_ch) {
    uint16_t s = lfsr16_at(seed, frame);        // стан рівно на цьому кадрі
    // (за потреби — через ту саму перестановну таблицю й фільтр)
    return chan_perm[s % N_CH];
}
