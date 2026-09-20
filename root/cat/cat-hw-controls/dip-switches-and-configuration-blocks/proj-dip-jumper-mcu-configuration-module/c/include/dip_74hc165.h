#ifndef DIP_74HC165_H
#define DIP_74HC165_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file dip_74hc165.h
 * @brief Драйвер зчитування 8-позиційного DIP-перемикача через 74HC165.
 */

/* Визначення умовних номерів виводів GPIO мікроконтролера */
#define GPIO_PIN_PL   5   /**< Вивід паралельного завантаження (Parallel Load / SH_LD) */
#define GPIO_PIN_CLK  6   /**< Вивід тактового сигналу (Clock) */
#define GPIO_PIN_DATA 7   /**< Вивід послідовних даних (Serial Output Q7) */

/* Бітові маски та зсуви для розбору 8-бітного конфігураційного байта */
#define DIP_SHIFT_ADDRESS 6
#define DIP_MASK_ADDRESS  (0xC0)  /**< Біти [7:6]: Системна адреса (0..3) */

#define DIP_SHIFT_BAUD    3
#define DIP_MASK_BAUD     (0x38)  /**< Біти [5:3]: Індекс швидкості зв'язку (0..7) */

#define DIP_SHIFT_FLAG_A  2
#define DIP_MASK_FLAG_A   (0x04)  /**< Біт 2: Прапорець додаткового режиму A */

#define DIP_SHIFT_FLAG_B  1
#define DIP_MASK_FLAG_B   (0x02)  /**< Біт 1: Прапорець додаткового режиму B */

#define DIP_MASK_PARITY   (0x01)  /**< Біт 0: Парність для перевірки цілісності */

/**
 * @brief Структура декодованих налаштувань DIP-перемикача.
 */
typedef struct {
    uint8_t system_address;  /**< Системна адреса пристрою (0..3) */
    uint8_t baud_rate_index; /**< Індекс швидкості передачі (0..7) */
    bool feature_flag_a;     /**< Стан прапорця режиму A */
    bool feature_flag_b;     /**< Стан прапорця режиму B */
    uint8_t raw_value;       /**< Сировий зчитаний байт */
    bool parity_valid;       /**< Прапорець успішної перевірки паритету */
} dip_config_t;

/**
 * @brief Ініціалізація виводів GPIO для роботи зі зсувним регістром 74HC165.
 */
void dip_74hc165_init(void);

/**
 * @brief Послідовне зчитування сирого 8-бітного байта з 74HC165.
 * @return Зчитаний 8-бітний конфігураційний байт.
 */
uint8_t dip_74hc165_read_raw(void);

/**
 * @brief Обчислення парності 8-бітного байта для контролю цілісності.
 * @param byte Байт для обчислення парності.
 * @return true, якщо кількість одиничних бітів парна.
 */
bool dip_74hc165_calculate_parity(uint8_t byte);

/**
 * @brief Розбір сирого байта на окремі поля конфігурації з перевіркою паритету.
 * @param raw_byte Сировий зчитаний байт з перемикачів.
 * @param config Вказівник на структуру для збереження розібраних полів.
 * @return true, якщо паритет збігається, інакше false.
 */
bool dip_74hc165_parse_config(uint8_t raw_byte, dip_config_t *config);

#endif /* DIP_74HC165_H */
