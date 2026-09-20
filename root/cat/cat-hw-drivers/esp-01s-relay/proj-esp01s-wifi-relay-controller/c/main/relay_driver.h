#ifndef RELAY_DRIVER_H
#define RELAY_DRIVER_H

#include <stdbool.h>
#include <stdint.h>
#include "driver/gpio.h"
#include "esp_err.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

/**
 * @file relay_driver.h
 * @brief Заголовочний файл низькорівневого драйвера силового реле для модуля ESP-01S.
 *
 * Модуль реалізує безпечне керування силовим реле, підключеним до лінії GPIO0.
 * Враховує особливості апаратної схеми ESP-01S Relay v1.0/v4.0 (Active LOW)
 * та забезпечує захист від хибного спрацьовування котушки реле під час старт-апу.
 */

/* Вивід GPIO0 за замовчуванням для модуля ESP-01S Relay */
#define RELAY_DEFAULT_GPIO_PIN GPIO_NUM_0

/**
 * @brief Стан силового реле.
 */
typedef enum {
    RELAY_STATE_OFF = 0, /* Реле вимкнено (контакти розімкнені) */
    RELAY_STATE_ON  = 1  /* Реле увімкнено (контакти замкнені) */
} relay_state_t;

/**
 * @brief Конфігураційна структура драйвера реле.
 */
typedef struct {
    gpio_num_t gpio_pin;         /* Номер GPIO виводу (за замовчуванням GPIO_NUM_0) */
    bool active_low;             /* Прапорець інверсної логіки (true для ESP-01S Relay module) */
    relay_state_t initial_state; /* Початковий стан при ініціалізації */
} relay_config_t;

/**
 * @brief Дескриптор драйвера реле.
 */
typedef struct {
    gpio_num_t gpio_pin;         /* Фізичний вивід GPIO */
    bool active_low;             /* Інверсна логіка (true: LOW = ON, HIGH = OFF) */
    relay_state_t current_state; /* Поточний збережений стан */
    bool is_initialized;         /* Прапорець завершення ініціалізації */
    SemaphoreHandle_t lock;      /* М'ютекс FreeRTOS для забезпечення потокобезпечності */
} relay_handle_t;

/**
 * @brief Первинна безпечна ініціалізація виводу GPIO0 та драйвера реле.
 *
 * @param handle Вказівник на дескриптор драйвера.
 * @param config Вказівник на структуру конфігурації.
 * @return ESP_OK у разі успіху, або відповідний код помилки.
 */
esp_err_t relay_driver_init(relay_handle_t *handle, const relay_config_t *config);

/**
 * @brief Встановлення нового стану силового реле.
 *
 * @param handle Вказівник на дескриптор драйвера.
 * @param state Бажаний стан (RELAY_STATE_ON або RELAY_STATE_OFF).
 * @return ESP_OK у разі успіху, або код помилки.
 */
esp_err_t relay_driver_set_state(relay_handle_t *handle, relay_state_t state);

/**
 * @brief Перемикання поточного стану силового реле на протилежний.
 *
 * @param handle Вказівник на дескриптор драйвера.
 * @return ESP_OK у разі успіху, або код помилки.
 */
esp_err_t relay_driver_toggle(relay_handle_t *handle);

/**
 * @brief Зчитування поточного стану силового реле.
 *
 * @param handle Вказівник на дескриптор драйвера.
 * @return Поточний стан (RELAY_STATE_ON або RELAY_STATE_OFF).
 */
relay_state_t relay_driver_get_state(relay_handle_t *handle);

/**
 * @brief Деініціалізація драйвера реле та звільнення ресурсів.
 *
 * @param handle Вказівник на дескриптор драйвера.
 * @return ESP_OK у разі успіху.
 */
esp_err_t relay_driver_deinit(relay_handle_t *handle);

#endif /* RELAY_DRIVER_H */
