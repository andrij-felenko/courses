#include "thumbwheel_74hc165.h"
#include <string.h>

thumbwheel_status_t thumbwheel_init(thumbwheel_driver_t *driver, const thumbwheel_config_t *config) {
    if (!driver || !config) {
        return THUMBWHEEL_ERR_INVALID_PARAM;
    }
    if (!config->set_pl || !config->set_clk || !config->read_q7 || !config->delay_us) {
        return THUMBWHEEL_ERR_INVALID_PARAM;
    }
    if (config->num_digits == 0 || config->num_digits > THUMBWHEEL_MAX_DIGITS) {
        return THUMBWHEEL_ERR_INVALID_PARAM;
    }

    memset(driver, 0, sizeof(thumbwheel_driver_t));
    driver->config = *config;
    driver->is_initialized = true;

    // Початковий пасивний стан ліній: PL = HIGH (фіксація знята), CLK = LOW
    driver->config.set_pl(true);
    driver->config.set_clk(false);

    return THUMBWHEEL_OK;
}

// Внутрішня функція побітового стробування 74HC165 та витягування бітів
static uint64_t thumbwheel_shift_in_bits(thumbwheel_driver_t *driver, uint8_t total_bits) {
    uint64_t raw_data = 0;

    // 1. Защелкування паралельних даних: короткий низький імпульс на лінію PL
    driver->config.set_pl(false);
    driver->config.delay_us(1); // Затримка t_PL_min (типово > 20 нс)
    driver->config.set_pl(true);
    driver->config.delay_us(1);

    // 2. Послідовне висування бітів через CLK (MSB або LSB залежно від підключення)
    for (int i = 0; i < total_bits; i++) {
        // Зчитуємо поточний біт із виходу Q7
        bool bit = driver->config.read_q7();
        raw_data = (raw_data << 1) | (bit ? 1ULL : 0ULL);

        // Тактовий імпульс CLK: LOW -> HIGH -> LOW
        driver->config.set_clk(true);
        driver->config.delay_us(1);
        driver->config.set_clk(false);
        driver->config.delay_us(1);
    }

    return raw_data;
}

// Мажоритарний фільтр (голосування більшості) для 1-ї тетради BCD
static uint8_t thumbwheel_majority_vote(const uint8_t *history, uint8_t depth) {
    uint8_t counts[16] = {0};
    uint8_t max_count = 0;
    uint8_t winner = 0xFF;

    for (uint8_t i = 0; i < depth; i++) {
        uint8_t val = history[i];
        if (val <= 9) { // Беремо до уваги тільки валідні BCD коди
            counts[val]++;
            if (counts[val] > max_count) {
                max_count = counts[val];
                winner = val;
            }
        }
    }

    // Переможець мусить набрати більше 50% голосів у буфері
    if (max_count > (depth / 2)) {
        return winner;
    }
    return 0xFF; // Нестабільний стан
}

thumbwheel_status_t thumbwheel_read_value(thumbwheel_driver_t *driver, uint32_t *out_value) {
    if (!driver || !out_value) {
        return THUMBWHEEL_ERR_INVALID_PARAM;
    }
    if (!driver->is_initialized) {
        return THUMBWHEEL_ERR_NOT_INIT;
    }

    // Кожен розряд перемикача дає 4 біти BCD
    uint8_t total_bits = driver->config.num_digits * 4;
    uint64_t raw_data = thumbwheel_shift_in_bits(driver, total_bits);

    // Розбір кадру на 4-бітні BCD-тетради
    uint8_t current_nibbles[THUMBWHEEL_MAX_DIGITS];
    bool has_transit_code = false;

    for (int digit = 0; digit < driver->config.num_digits; digit++) {
        // Виділяємо тетраду (4 біти)
        uint8_t shift_amount = (driver->config.num_digits - 1 - digit) * 4;
        uint8_t nibble = (uint8_t)((raw_data >> shift_amount) & 0x0F);

        // Якщо перемикач прямого BCD (active_low), інвертуємо біти тетради
        if (driver->config.active_low_logic) {
            nibble = (~nibble) & 0x0F;
        }

        // Перевірка BCD-діапазону: значення 10..15 є транзитними некоректними станами
        if (nibble > 9) {
            has_transit_code = true;
        }
        current_nibbles[digit] = nibble;
    }

    // Запис у кільцевий буфер історії фільтрації
    uint8_t idx = driver->filter_index;
    for (int digit = 0; digit < driver->config.num_digits; digit++) {
        driver->raw_history[digit][idx] = current_nibbles[digit];
    }
    driver->filter_index = (idx + 1) % THUMBWHEEL_FILTER_DEPTH;

    // Якщо під час поточного кадтування виявлено транзитний код, утримуємо останнє валідне значення
    if (has_transit_code) {
        *out_value = driver->last_valid_value;
        return THUMBWHEEL_ERR_TRANSIT_CODE;
    }

    // Проведення мажоритарної фільтрації по кожному розряду
    uint32_t result_value = 0;
    for (int digit = 0; digit < driver->config.num_digits; digit++) {
        uint8_t voted_digit = thumbwheel_majority_vote(driver->raw_history[digit], THUMBWHEEL_FILTER_DEPTH);
        if (voted_digit > 9) {
            // Фільтр ще не стабілізувався — повертаємо підтверджене значення
            *out_value = driver->last_valid_value;
            return THUMBWHEEL_ERR_TRANSIT_CODE;
        }
        // Збирання десяткового числа з ваговими коефіцієнтами декад
        result_value = result_value * 10 + voted_digit;
    }

    driver->last_valid_value = result_value;
    *out_value = result_value;
    return THUMBWHEEL_OK;
}
