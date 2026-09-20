#include <stdio.h>
#include "../include/dip_74hc165.h"

/* Таблиця стандартних швидкостей baud rate за індексом */
static const uint32_t BAUD_RATE_TABLE[8] = {
    9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600
};

int main(void) {
    printf("Ініціалізація драйвера DIP-перемикачів 74HC165...\n");
    dip_74hc165_init();

    /* Зчитування сирого конфігураційного байта */
    uint8_t raw_val = dip_74hc165_read_raw();
    printf("Зчитано сирий байт з DIP-перемикача: 0x%02X\n", raw_val);

    dip_config_t config;
    bool status = dip_74hc165_parse_config(raw_val, &config);

    if (!status) {
        printf("ПОМИЛКА: Перевірка паритету не пройдена! Застосовуються безпечні налаштування за замовчуванням.\n");
        config.system_address = 0;
        config.baud_rate_index = 0;
        config.feature_flag_a = false;
        config.feature_flag_b = false;
    } else {
        printf("Конфігурацію успішно верифіковано (паритет OK).\n");
    }

    /* Застосування налаштувань у системі */
    uint32_t selected_baud = BAUD_RATE_TABLE[config.baud_rate_index & 0x07];
    printf("--- Застосовані налаштування системи ---\n");
    printf("  Системна адреса (Address): %u\n", config.system_address);
    printf("  Швидкість зв'язку (Baud Rate): %u біт/с (індекс %u)\n", selected_baud, config.baud_rate_index);
    printf("  Режим A (Feature A): %s\n", config.feature_flag_a ? "УВІМКНЕНО" : "ВИМКНЕНО");
    printf("  Режим B (Feature B): %s\n", config.feature_flag_b ? "УВІМКНЕНО" : "ВИМКНЕНО");
    printf("---------------------------------------\n");

    return 0;
}
