#ifndef TOGGLE_SWITCH_H
#define TOGGLE_SWITCH_H

#include "toggle_switch_types.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"

// Структура об'єкта драйвера тумблера
typedef struct toggle_switch_handle_s* toggle_switch_handle_t;

// Ініціалізація тумблера під ESP-IDF та створення черги подій
esp_err_t toggle_switch_init(const toggle_switch_config_t *config, 
                           QueueHandle_t event_queue, 
                           toggle_switch_handle_t *out_handle);

// Отримання поточного миттєвого відфільтрованого стану
toggle_switch_state_t toggle_switch_get_state(toggle_switch_handle_t handle);

// Деініціалізація драйвера та звільнення ресурсів
esp_err_t toggle_switch_deinit(toggle_switch_handle_t handle);

#endif // TOGGLE_SWITCH_H
