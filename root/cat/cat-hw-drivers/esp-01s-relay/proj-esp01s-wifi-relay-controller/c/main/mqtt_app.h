#ifndef MQTT_APP_H
#define MQTT_APP_H

#include "esp_err.h"
#include "relay_driver.h"
#include "mqtt_client.h"

/**
 * @file mqtt_app.h
 * @brief Заголовочний файл MQTT-клієнта для ESP8266 RTOS SDK / ESP-IDF.
 *
 * Забезпечує неблокуючий обмін повідомленнями з MQTT-брокером:
 * підписка на топік команд керування реле та публікація зворотної телеметрії.
 */

/* Назви MQTT-топіків за замовчуванням */
#define MQTT_TOPIC_COMMAND "esp01s/relay/cmd"
#define MQTT_TOPIC_STATUS  "esp01s/relay/state"

/**
 * @brief Конфігурація MQTT-клієнта.
 */
typedef struct {
    char broker_uri[128];         /* URI брокера (наприклад, "mqtt://192.168.1.100:1883") */
    char client_id[32];           /* Унікальний ідентифікатор клієнта */
    char username[32];            /* Логін MQTT (якщо потрібна авторизація) */
    char password[64];            /* Пароль MQTT */
    relay_handle_t *relay_handle; /* Вказівник на дескриптор керування реле */
} mqtt_app_config_t;

/**
 * @brief Запуск MQTT-клієнта та неблокуючої задачи обробки мережевих пакетів.
 *
 * @param config Вказівник на структуру конфігурації.
 * @return ESP_OK у разі успіху, або код помилки.
 */
esp_err_t mqtt_app_start(const mqtt_app_config_t *config);

/**
 * @brief Зворотна публікація поточного стану реле у MQTT-топік статусу.
 *
 * @param state Стан реле для публікації.
 * @return ESP_OK у разі успіху.
 */
esp_err_t mqtt_app_publish_status(relay_state_t state);

/**
 * @brief Зупинка MQTT-клієнта та розрив з'єднання.
 *
 * @return ESP_OK у разі успіху.
 */
esp_err_t mqtt_app_stop(void);

#endif /* MQTT_APP_H */
