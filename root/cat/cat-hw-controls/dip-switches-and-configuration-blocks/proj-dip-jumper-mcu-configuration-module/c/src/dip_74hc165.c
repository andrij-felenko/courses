#include "../include/dip_74hc165.h"
#include <stdio.h>

/* Абстракція низькорівневих функцій роботи з GPIO */
static void gpio_set_mode_output(uint8_t pin) {
    (void)pin;
    /* Ініціалізація виводу як виходу */
}

static void gpio_set_mode_input(uint8_t pin) {
    (void)pin;
    /* Ініціалізація виводу як входу з підтяжкою */
}

static void gpio_write(uint8_t pin, bool level) {
    (void)pin;
    (void)level;
    /* У реальній системі: запис рівня на вивід GPIO */
}

static bool gpio_read(uint8_t pin) {
    (void)pin;
    /* У реальній системі: зчитування логічного рівня з виводу GPIO */
    return true;
}

static void delay_us(uint32_t us) {
    (void)us;
    /* Програмна затримка в мікросекундах */
}

void dip_74hc165_init(void) {
    gpio_set_mode_output(GPIO_PIN_PL);
    gpio_set_mode_output(GPIO_PIN_CLK);
    gpio_set_mode_input(GPIO_PIN_DATA);

    /* Початковий стан: PL в HIGH (режим зсуву), CLK в LOW */
    gpio_write(GPIO_PIN_PL, true);
    gpio_write(GPIO_PIN_CLK, false);
}

uint8_t dip_74hc165_read_raw(void) {
    uint8_t raw_byte = 0;

    /* Крок 1: Формування низького імпульсу засувки PL для фіксації паралельних входів */
    gpio_write(GPIO_PIN_PL, false);
    delay_us(2); /* Затримка для гарантованого завантаження (t_w >= 20 нс) */
    gpio_write(GPIO_PIN_PL, true);
    delay_us(1);

    /* Крок 2: Послідовне зчитування 8 бітів починаючи зі старшого D7 */
    for (int8_t i = 7; i >= 0; i--) {
        bool bit_val = gpio_read(GPIO_PIN_DATA);
        if (bit_val) {
            raw_byte |= (uint8_t)(1U << i);
        }

        /* Тактовий імпульс CLK для зсуву наступного біта на вихід Q7 */
        gpio_write(GPIO_PIN_CLK, true);
        delay_us(1);
        gpio_write(GPIO_PIN_CLK, false);
        delay_us(1);
    }

    return raw_byte;
}

bool dip_74hc165_calculate_parity(uint8_t byte) {
    uint8_t count = 0;
    for (uint8_t i = 0; i < 8; i++) {
        if ((byte >> i) & 0x01) {
            count++;
        }
    }
    /* Повертає true, якщо кількість встановлених бітів є парною */
    return (count % 2) == 0;
}

bool dip_74hc165_parse_config(uint8_t raw_byte, dip_config_t *config) {
    if (config == NULL) {
        return false;
    }

    config->raw_value = raw_byte;

    /* Виділення суб-полів побітовими масками й зсувом праворуч */
    config->system_address  = (raw_byte & DIP_MASK_ADDRESS) >> DIP_SHIFT_ADDRESS;
    config->baud_rate_index = (raw_byte & DIP_MASK_BAUD) >> DIP_SHIFT_BAUD;
    config->feature_flag_a  = (raw_byte & DIP_MASK_FLAG_A) != 0;
    config->feature_flag_b  = (raw_byte & DIP_MASK_FLAG_B) != 0;

    /* Перевірка цілісності даних за паритетом */
    config->parity_valid = dip_74hc165_calculate_parity(raw_byte);

    return config->parity_valid;
}
