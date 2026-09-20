#ifndef ROTARY_ADC_SELECTOR_H
#define ROTARY_ADC_SELECTOR_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/** Кількість фізичних позицій галетного перемикача */
#define ROTARY_SELECTOR_POSITIONS   12

/** Розмір буфера для медіанного фільтра */
#define ROTARY_MEDIAN_WINDOW_SIZE   3

/**
 * @brief Перелік станів роботи драйвера та діагностики помилок
 */
typedef enum {
    ROTARY_STATUS_OK = 0,               /**< Нормальна робота: виявлено валідну позицію */
    ROTARY_STATUS_ERR_OPEN_CIRCUIT,     /**< Аварія: обрив шлейфу (напруга вище верхнього порога) */
    ROTARY_STATUS_ERR_SHORT_GND,        /**< Аварія: коротке замикання на земляний провід (напруга нижче нижнього порога) */
    ROTARY_STATUS_ERR_OUT_OF_RANGE,     /**< Аварія: значення напруги потрапляє в невизначену зону між позиціями */
    ROTARY_STATUS_ERR_INVALID_ARG       /**< Помилка аргументів ініціалізації */
} rotary_status_t;

/**
 * @brief Структура конфігурації еталонних рівнів напруги (у відліках АЦП)
 */
typedef struct {
    uint16_t reference_levels[ROTARY_SELECTOR_POSITIONS]; /**< Масив із 12 еталонних відліків АЦП */
    uint16_t hysteresis_window;    /**< Ширина вікна цифрового гістерезису (в відліках АЦП) */
    uint16_t min_valid_adc;         /**< Нижній поріг валідності (ніжче цього — КЗ на GND) */
    uint16_t max_valid_adc;         /**< Верхній поріг валідності (вище цього — обрив лінії VCC) */
} rotary_config_t;

/**
 * @brief Структура дескриптора стану драйвера
 */
typedef struct {
    rotary_config_t config;                                /**< Копія конфігураційних параметрів */
    uint16_t median_buffer[ROTARY_MEDIAN_WINDOW_SIZE];    /**< Кільцевий буфер для медіанної фільтрації */
    uint8_t buffer_index;                                  /**< Поточний індекс у буфері */
    bool buffer_filled;                                    /**< Прапорець заповнення буфера */
    int8_t current_position;                               /**< Поточна підтверджена позиція (0..11 або -1 при помилці) */
    rotary_status_t last_status;                           /**< Останній діагностичний статус */
} rotary_selector_t;

/**
 * @brief Ініціалізація драйвера аналогового галетного перемикача
 * @param handle Вказівник на дескриптор драйвера
 * @param config Вказівник на структуру конфігурації
 * @return ROTARY_STATUS_OK у разі успіху або відповідний код помилки
 */
rotary_status_t rotary_selector_init(rotary_selector_t *handle, const rotary_config_t *config);

/**
 * @brief Неблокуюче опитування та декодування стану за новим відліком АЦП
 * @param handle Вказівник на дескриптор драйвера
 * @param raw_adc Сирий відлік АЦП від мікроконтролера
 * @param out_position Вихідний вказівник для збереження визначеної позиції (0..11)
 * @return rotary_status_t Статус діагностики лінії та декодування
 */
rotary_status_t rotary_selector_update(rotary_selector_t *handle, uint16_t raw_adc, int8_t *out_position);

#ifdef __cplusplus
}
#endif

#endif /* ROTARY_ADC_SELECTOR_H */
