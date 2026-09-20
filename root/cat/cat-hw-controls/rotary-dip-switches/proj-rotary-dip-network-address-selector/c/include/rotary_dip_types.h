#ifndef ROTARY_DIP_TYPES_H
#define ROTARY_DIP_TYPES_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Типи кодування ротаційного DIP-перемикача.
 */
typedef enum {
    ROTARY_DIP_ENCODING_BCD  = 0, /**< Двійково-десятковий код (0..9) */
    ROTARY_DIP_ENCODING_HEX  = 1, /**< Шістнадцятковий код (0..F) */
    ROTARY_DIP_ENCODING_GRAY = 2  /**< Код Ґрея (0..F) */
} rotary_dip_encoding_t;

/**
 * @brief Режими апаратної підтяжки сигнальних ліній GPIO.
 */
typedef enum {
    ROTARY_DIP_PULL_UP   = 0, /**< Підтяжка до VCC (активний рівень LOW, замкнено = 0) */
    ROTARY_DIP_PULL_DOWN = 1  /**< Підтяжка до GND (активний рівень HIGH, замкнено = 1) */
} rotary_dip_pull_mode_t;

/**
 * @brief Опис підключення одного бітового контакту (біти 0..3: 1, 2, 4, 8).
 */
typedef struct {
    uint8_t port_id;   /**< Ідентифікатор GPIO порту (PORTA = 0, PORTB = 1, тощо) */
    uint8_t pin_index; /**< Номер ніжки в порту (0..31) */
} rotary_dip_pin_t;

/**
 * @brief Конфігурація ротаційного DIP-перемикача.
 */
typedef struct {
    rotary_dip_pin_t pins[4];         /**< Масив ніжок для бітів 0, 1, 2, 3 (ваги 1, 2, 4, 8) */
    rotary_dip_pull_mode_t pull_mode; /**< Режим підтяжки ліній */
    rotary_dip_encoding_t encoding;   /**< Формат кодування списку станів */
    uint32_t debounce_ms;             /**< Затримка для антидребезгу в мілісекундах */
} rotary_dip_config_t;

/**
 * @brief Контекст драйвера ротаційного DIP-перемикача.
 */
typedef struct {
    rotary_dip_config_t config;   /**< Копія конфігурації пристрою */
    uint8_t raw_code;             /**< Сирий відчитаний бітовий стан ліній (0x00..0x0F) */
    uint8_t decoded_value;        /**< Декодоване числове значення (0..15 або 0..9) */
    bool is_valid;                /**< Прапорець коректності (false при перевищенні в BCD) */
    uint32_t last_read_timestamp; /**< Часова мітка останньої зміни для програмного антидребезгу */
} rotary_dip_t;

#endif /* ROTARY_DIP_TYPES_H */
