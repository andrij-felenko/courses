#include "st7789.h"

/**
 * @brief Надіслати 8-бітний код команди на дисплей ST7789.
 * @param dev Покажчик на ініціалізований дескриптор пристрою.
 * @param cmd Код інструкції (наприклад, 0x2A для CASET).
 */
void st7789_write_cmd(st7789_t *dev, uint8_t cmd) {
    /* Перемикаємо D/C у низький рівень (режим команди) */
    dev->set_dc(0, dev->user_data);

    /* Активуємо вибір чипа (CS -> LOW) */
    dev->set_cs(0, dev->user_data);

    /* Передаємо байт команди */
    dev->spi_write(&cmd, 1, dev->user_data);

    /* Деактивуємо вибір чипа (CS -> HIGH) для завершення команди */
    dev->set_cs(1, dev->user_data);
}

/**
 * @brief Надіслати послідовність байтів даних або параметрів на дисплей.
 * @param dev Покажчик на дескриптор пристрою.
 * @param data Покажчик на буфер із даними.
 * @param len Кількість байтів для передачі.
 */
void st7789_write_data(st7789_t *dev, const uint8_t *data, size_t len) {
    if (len == 0 || data == NULL) {
        return;
    }

    /* Перемикаємо D/C у високий рівень (режим даних) */
    dev->set_dc(1, dev->user_data);

    /* Активуємо вибір чипа (CS -> LOW) */
    dev->set_cs(0, dev->user_data);

    /* Передаємо масив даних */
    dev->spi_write(data, len, dev->user_data);

    /* Деактивуємо вибір чипа (CS -> HIGH) */
    dev->set_cs(1, dev->user_data);
}

/**
 * @brief Надіслати один байт параметра поточної команди.
 * @param dev Покажчик на дескриптор пристрою.
 * @param byte Значення байта.
 */
void st7789_write_data_byte(st7789_t *dev, uint8_t byte) {
    st7789_write_data(dev, &byte, 1);
}
