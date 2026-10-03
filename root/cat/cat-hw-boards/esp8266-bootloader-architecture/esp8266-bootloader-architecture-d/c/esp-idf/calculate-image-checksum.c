#include <stdint.h>
#include <stdbool.h>

/* Структура конфігураційного сектора rboot у флеш-пам'яті (адреса 0x02000) */
typedef struct {
    uint8_t magic;          /* Магічний байт конфігурації rboot (0x05) */
    uint8_t version;        /* Версія структури заголовка */
    uint8_t mode;           /* Режим роботи (0 = стандартний, 1 = gpio sel) */
    uint8_t current_rom;    /* Індекс поточного активного слота (0 або 1) */
    uint8_t gpio_rom0;      /* Номер GPIO для апаратного вибору слота 0 */
    uint8_t count;          /* Загальна кількість доступних слотів */
    uint8_t boot_once;      /* Прапорець пробного запуску для перевірки FOTA */
    uint8_t roms[4];        /* Масив фізичних адрес слотів у флеш-пам'яті */
    uint32_t roms_sizes[4]; /* Масив максимальних розмірів слотів у байтах */
} rboot_config_t;

/* Обчислення 8-бітної XOR контрольної суми бінарного образу */
uint8_t calculate_image_checksum(const uint8_t *data, uint32_t length) {
    uint8_t chksum = 0xEF; /* Початковий константний базіс алгоритму Espressif */
    for (uint32_t i = 0; i < length; i++) {
        chksum ^= data[i];
    }
    return chksum;
}

/* Перевірка цілісності слота та підготовка до автоматичного відкочування */
bool verify_and_switch_slot(rboot_config_t *config, uint8_t target_slot, const uint8_t *img_data, uint32_t img_len, uint8_t expected_chksum) {
    /* Перевірка відповідності контрольної суми зчитаних даних */
    uint8_t computed_chksum = calculate_image_checksum(img_data, img_len);
    if (computed_chksum != expected_chksum) {
        /* Контрольна сума не збігається: оновлення відхиляється, залишається поточний слот */
        return false;
    }

    /* Встановлення прапорця пробного запуску для відкочування в разі збою */
    config->current_rom = target_slot;
    config->boot_once = 1; /* Якщо наступний запуск впаде, rboot поверне попередній ROM */

    return true;
}
