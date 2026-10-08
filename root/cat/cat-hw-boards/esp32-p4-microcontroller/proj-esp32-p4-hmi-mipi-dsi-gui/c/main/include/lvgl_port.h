#ifndef LVGL_PORT_H
#define LVGL_PORT_H

#include <stdint.h>
#include <stdbool.h>
#include "esp_err.h"
#include "mipi_dsi_ppa_driver.h"
#include "lvgl.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Структура конфігурації порту LVGL
 */
typedef struct {
    frame_buffer_descriptor_t *fb_descriptor; /*!< Указник на дескриптор подвійного фреймбуфера PSRAM */
    uint32_t hor_res;                          /*!< Горизонтальна роздільна здатність */
    uint32_t ver_res;                          /*!< Вертикальна роздільна здатність */
    uint32_t tick_period_ms;                   /*!< Період таймера lv_tick_inc в мілісекундах */
    uint32_t task_priority;                    /*!< Пріоритет задачі FreeRTOS для обробки LVGL */
    uint32_t task_stack_size;                  /*!< Розмір стека задачі FreeRTOS в байтах */
} lvgl_port_config_t;

/**
 * @brief Непрозорий дескриптор об'єкта порту LVGL
 */
typedef struct lvgl_port_context_t *lvgl_port_handle_t;

/**
 * @brief Ініціалізація графічної бібліотеки LVGL та її прив'язка до апаратних драйверів
 *
 * @param cfg Конфігураційні параметри порту
 * @param handle Указник для збереження створеного дескриптора
 * @return esp_err_t ESP_OK у разі успіху
 */
esp_err_t lvgl_port_init(const lvgl_port_config_t *cfg, lvgl_port_handle_t *handle);

/**
 * @brief Запуск періодичного апаратного таймера для відліку системного часу LVGL (lv_tick_inc)
 *
 * @param period_ms Період спрацьовування таймера у мілісекундах
 * @return esp_err_t ESP_OK у разі успіху
 */
esp_err_t lvgl_port_init_tick(uint32_t period_ms);

/**
 * @brief Функція зворотного виклику промальовки LVGL (flush_cb) з використанням прискорення PPA
 *
 * @param drv Указник на дисплейний драйвер LVGL
 * @param area Задана область екрана для оновлення
 * @param color_p Буфер пікселів від промальовщика LVGL
 */
void lvgl_port_flush_callback(lv_disp_drv_t *drv, const lv_area_t *area, lv_color_t *color_p);

/**
 * @brief Головна задача FreeRTOS для періодичного виклику lv_timer_handler()
 *
 * @param arg Вхідний аргумент (контекст порту)
 */
void lvgl_port_task(void *arg);

/**
 * @brief Зупинка та деініціалізація порту LVGL
 *
 * @param handle Дескриптор порту
 * @return esp_err_t ESP_OK у разі успіху
 */
esp_err_t lvgl_port_deinit(lvgl_port_handle_t handle);

#ifdef __cplusplus
}
#endif

#endif /* LVGL_PORT_H */
