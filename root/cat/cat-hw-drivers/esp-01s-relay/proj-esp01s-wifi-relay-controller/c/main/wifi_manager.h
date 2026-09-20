#ifndef WIFI_MANAGER_H
#define WIFI_MANAGER_H

#include <stdbool.h>
#include <stdint.h>
#include "esp_err.h"
#include "esp_event.h"
#include "esp_wifi.h"
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"

/**
 * @file wifi_manager.h
 * @brief Заголовочний файл мережевого менеджера Wi-Fi для ESP8266 RTOS SDK / ESP-IDF.
 *
 * Модуль відповідає за неблокуюче підключення до Wi-Fi у режимі Station,
 * автоматичне перепідключення при втраті з'єднання та сигналізацію стану через FreeRTOS Event Group.
 */

/* Бит Event Group: Wi-Fi успішно підключено та отримано IP-адресу */
#define WIFI_CONNECTED_BIT BIT0

/* Бит Event Group: вичерпано максимальну кількість спроб підключення */
#define WIFI_FAIL_BIT      BIT1

/**
 * @brief Структура конфігурації підключення Wi-Fi.
 */
typedef struct {
    char ssid[32];          /* Назва мережі Wi-Fi (SSID) */
    char password[64];      /* Пароль до мережі Wi-Fi */
    uint8_t max_retry;      /* Максимальна кількість спроб підключення поспіль */
} wifi_manager_config_t;

/**
 * @brief Ініціалізація та запуск мережевого підключення Wi-Fi station.
 *
 * @param config Вказівник на структуру конфігурації Wi-Fi.
 * @return ESP_OK у разі успіху, або відповідний код помилки.
 */
esp_err_t wifi_manager_init(const wifi_manager_config_t *config);

/**
 * @brief Отримання вказівника на FreeRTOS Event Group Wi-Fi менеджера.
 *
 * @return EventGroupHandle_t Дескриптор групи подій.
 */
EventGroupHandle_t wifi_manager_get_event_group(void);

/**
 * @brief Перевірка поточного стану з'єднання Wi-Fi.
 *
 * @return true, якщо пристрій підключений до AP та має IP-адресу, інакше false.
 */
bool wifi_manager_is_connected(void);

/**
 * @brief Зупинка та деініціалізація Wi-Fi стека.
 *
 * @return ESP_OK у разі успіху.
 */
esp_err_t wifi_manager_stop(void);

#endif /* WIFI_MANAGER_H */
