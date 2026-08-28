#ifndef BSP_INTERFACE_H
#define BSP_INTERFACE_H

#include "bsp_types.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Повна ініціалізація апаратної плати.
 * 
 * Конфігурує системне тактування мікроконтролера, налаштовує стандартні стани
 * ліній GPIO, ініціалізує шини I2C/SPI, вимикає невикористані силові ключі.
 * 
 * @return BSP_STATUS_OK у разі успіху, або код помилки периферії.
 */
bsp_status_t board_init(void);

/**
 * @brief Деініціалізація та повернення плати у вихідний безпечний стан.
 */
bsp_status_t board_deinit(void);

/**
 * @brief Керування станом системного світлодіода.
 * 
 * Автоматично враховує схемотехнічну полярність (Active-High / Active-Low)
 * та режим виводу (Push-Pull / Open-Drain).
 * 
 * @param led   Ідентифікатор світлодіода.
 * @param state Бажаний логічний стан (ON / OFF).
 */
bsp_status_t board_led_set(board_led_id_t led, board_led_state_t state);

/**
 * @brief Перемикання стану світлодіода на протилежний.
 */
bsp_status_t board_led_toggle(board_led_id_t led);

/**
 * @brief Комутація живлення визначеного периферійного домену.
 * 
 * Керує затвором силового ключа (P-MOSFET / перемикач навантаження), витримує
 * обов'язкову затримку заряду блокувальних конденсаторів та переводить лінії
 * комунікаційних шин у високоімпедансний стан при вимкненні (для захисту від витоків).
 * 
 * @param domain Ідентифікатор домену живлення.
 * @param enable true — увімкнути живлення, false — знеструмити домен.
 */
bsp_status_t board_power_domain_set(board_power_domain_t domain, bool enable);

/**
 * @brief Зчитування поточних метрик акумуляторної батареї.
 * 
 * Запускає вимірювання АЦП, калібрує результат за внутрішнім джерелом опорної напруги
 * Vrefint, перераховує коефіцієнт резистивного дільника та обчислює залишковий відсоток.
 * 
 * @param[out] out_metrics Покажчик на вихідну структуру метрик.
 */
bsp_status_t board_get_battery_metrics(board_battery_metrics_t *out_metrics);

/**
 * @brief Отримання комплексних кліматичних метрик від сенсорів плати.
 * 
 * Виконує опитування фізичних мікросхем сенсорів (наприклад, BME280 / SHT30)
 * через шину I2C, обробляє та перевіряє контрольні суми і повертає готові фізичні дані.
 * 
 * @param[out] out_env Покажчик на структуру кліматичних вимірювань.
 */
bsp_status_t board_read_environment(board_env_metrics_t *out_env);

/**
 * @brief Переведення плати у режим глибокого сну.
 * 
 * Вимикає живлення зовнішніх сенсорів, конфігурує виводи в аналоговий режим (Hi-Z),
 * налаштовує джерело пробудження (RTC таймер або зовнішня кнопка) та зупиняє ядро MCU.
 * 
 * @param mode       Режим сну (Light / Deep).
 * @param timeout_ms Час сну в мілісекундах (0 — сон до зовнішнього переривання).
 */
bsp_status_t board_enter_low_power(board_sleep_mode_t mode, uint32_t timeout_ms);

/**
 * @brief Отримання монотонного системного часу від старту плати.
 * @return Час у мілісекундах.
 */
uint32_t board_get_tick_ms(void);

/**
 * @brief Блокуюча калібрована мікросекундна затримка.
 */
void board_delay_us(uint32_t us);

#ifdef __cplusplus
}
#endif

#endif /* BSP_INTERFACE_H */
