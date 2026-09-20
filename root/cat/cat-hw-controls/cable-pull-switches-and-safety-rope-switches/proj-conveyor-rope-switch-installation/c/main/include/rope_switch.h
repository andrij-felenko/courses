#ifndef ROPE_SWITCH_H
#define ROPE_SWITCH_H

#include <stdint.h>
#include <stdbool.h>
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Перелік станів тросового вимикача безпеки (IEC 60947-5-5)
 */
typedef enum {
    ROPE_SWITCH_STATE_OK = 0,             /**< Нормальний стан: трос натягнутий, два NC канали замкнені */
    ROPE_SWITCH_STATE_TRIPPED,            /**< Аварійне зупинення: трос потягнуто або обірвано (обидва канали розімкнені) */
    ROPE_SWITCH_STATE_FAULT_DISCREPANCY,  /**< Апаратна відмова: розбіжність сигналів між каналами > t_discrepancy */
    ROPE_SWITCH_STATE_WAIT_RESET          /**< Очікування скиду: лінії відновлено, очікується натискання кнопки Reset */
} rope_switch_state_t;

/**
 * @brief Структура конфігурації двоканального вимикача
 */
typedef struct {
    gpio_num_t ch1_pin;            /**< GPIO пін NC каналу 1 */
    gpio_num_t ch2_pin;            /**< GPIO пін NC каналу 2 */
    gpio_num_t reset_btn_pin;      /**< GPIO пін кнопки скиду (NO, active-low) */
    gpio_num_t status_led_pin;     /**< GPIO пін індикатора стану (аварія/норма) */
    uint32_t discrepancy_ms;       /**< Максимально допустимий час розсинхронізації каналів (мс) */
    uint32_t debounce_ms;          /**< Час антибрязкотної фільтрації (мс) */
} rope_switch_config_t;

/**
 * @brief Подія переривання GPIO каналу
 */
typedef struct {
    gpio_num_t pin;
    uint32_t timestamp_ms;
    int level;
} rope_switch_evt_t;

/**
 * @brief Ініціалізація драйвера тросового вимикача
 * @param config Вказівник на структуру конфігурації
 * @return esp_err_t ESP_OK при успішній ініціалізації
 */
esp_err_t rope_switch_init(const rope_switch_config_t *config);

/**
 * @brief Отримання поточного стану системи безпеки
 * @return rope_switch_state_t Поточний стан кінцевого автомата
 */
rope_switch_state_t rope_switch_get_state(void);

/**
 * @brief Отримання текстового опису стану системи
 * @param state Стан вимикача
 * @return const char* Текстовий рядок
 */
const char* rope_switch_state_to_str(rope_switch_state_t state);

#ifdef __cplusplus
}
#endif

#endif // ROPE_SWITCH_H
