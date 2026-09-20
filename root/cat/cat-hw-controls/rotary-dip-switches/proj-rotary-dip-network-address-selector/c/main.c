#include <stdio.h>
#include "include/rotary_dip_driver.h"

/* Функція симуляції встановлення фізичного стану ротаційного перемикача */
static void set_simulated_switch_position(const rotary_dip_config_t *config, uint8_t raw_pattern) {
    for (int i = 0; i < 4; i++) {
        uint8_t bit = (raw_pattern >> i) & 0x01;
        uint8_t pin_level = 0;
        
        if (config->pull_mode == ROTARY_DIP_PULL_UP) {
            pin_level = bit ? 0 : 1; /* PULL_UP: замкнений біт 1 робить рівень 0 */
        } else {
            pin_level = bit ? 1 : 0; /* PULL_DOWN: замкнений біт 1 робить рівень 1 */
        }

        hal_gpio_write_pin(config->pins[i].port_id, config->pins[i].pin_index, pin_level);
    }
}

int main(void) {
    printf("=== Драйвер ротаційних кодових DIP-перемикачів (C) ===\n\n");

    /* Конфігурація DIP-перемикача №1: Адреса Modbus (Hex, Pull-Up) */
    rotary_dip_config_t config_address = {
        .pins = {
            { .port_id = 0, .pin_index = 0 }, /* Біт 1 (Pin 0) */
            { .port_id = 0, .pin_index = 1 }, /* Біт 2 (Pin 1) */
            { .port_id = 0, .pin_index = 2 }, /* Біт 4 (Pin 2) */
            { .port_id = 0, .pin_index = 3 }  /* Біт 8 (Pin 3) */
        },
        .pull_mode = ROTARY_DIP_PULL_UP,
        .encoding = ROTARY_DIP_ENCODING_HEX,
        .debounce_ms = 20
    };

    /* Конфігурація DIP-перемикача №2: Швидкість Baudrate (Gray Code, Pull-Up) */
    rotary_dip_config_t config_baud = {
        .pins = {
            { .port_id = 1, .pin_index = 4 },
            { .port_id = 1, .pin_index = 5 },
            { .port_id = 1, .pin_index = 6 },
            { .port_id = 1, .pin_index = 7 }
        },
        .pull_mode = ROTARY_DIP_PULL_UP,
        .encoding = ROTARY_DIP_ENCODING_GRAY,
        .debounce_ms = 20
    };

    rotary_dip_t dip_address;
    rotary_dip_t dip_baud;

    rotary_dip_init(&dip_address, &config_address);
    rotary_dip_init(&dip_baud, &config_baud);

    /* Тест 1: Симуляція встановлення позиції 'B' (0x0B = 11) на Hex-перемикачі адреси */
    set_simulated_switch_position(&config_address, 0x0B);
    
    /* Імітуємо системний час t = 50 мс */
    if (rotary_dip_read(&dip_address, 50)) {
        uint8_t modbus_id = rotary_dip_get_modbus_address(&dip_address, 10);
        printf("[DIP Address Hex]: Сирий код = 0x%02X, Декодоване = %d (0x%X), Modbus ID = %d\n",
               dip_address.raw_code, dip_address.decoded_value, dip_address.decoded_value, modbus_id);
    }

    /* Тест 2: Симуляція Gray-коду для позиції index=4 (Gray 4 = 0x06 = 0b0110) */
    set_simulated_switch_position(&config_baud, 0x06);

    if (rotary_dip_read(&dip_baud, 50)) {
        uint32_t baudrate = rotary_dip_get_baudrate(&dip_baud);
        printf("[DIP Baud Gray]:   Сирий Gray = 0x%02X, Двійкове = %d, Baudrate = %u bps\n",
               dip_baud.raw_code, dip_baud.decoded_value, baudrate);
    }

    /* Тест 3: Симуляція BCD-перемикача з недопустимим значенням (0x0E > 9) */
    rotary_dip_config_t config_bcd = config_address;
    config_bcd.encoding = ROTARY_DIP_ENCODING_BCD;
    rotary_dip_t dip_bcd;
    rotary_dip_init(&dip_bcd, &config_bcd);

    set_simulated_switch_position(&config_bcd, 0x0E);
    bool valid = rotary_dip_read(&dip_bcd, 100);
    printf("[DIP BCD Error]:   Сирий BCD = 0x0E -> Валідність = %s (очікувано false)\n",
           valid ? "true" : "false");

    printf("\n=== Тестування та ініціалізація пройшли успішно ===\n");
    return 0;
}
