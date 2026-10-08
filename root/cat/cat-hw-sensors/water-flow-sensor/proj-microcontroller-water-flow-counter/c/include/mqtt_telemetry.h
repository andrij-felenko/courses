#ifndef MQTT_TELEMETRY_H
#define MQTT_TELEMETRY_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "water_flow_sensor.h"

/**
 * @file mqtt_telemetry.h
 * @brief Оголошення MQTT-модуля для форматування та передачі телеметрії водоспоживання у JSON.
 */

/** @brief Максимальна довжина JSON телеметричного пакета */
#define MQTT_MAX_PAYLOAD_LEN 256

/**
 * @brief Структура телеметричних даних для публікації.
 */
typedef struct {
    float flow_rate_lpm;          /**< Миттєва витрата (л/хв) */
    double total_volume_liters;   /**< Сумарний об'єм (літри) */
    uint64_t total_pulses;        /**< Лічильник імпульсів Холла */
    bool power_good;              /**< Статус основної мережі живлення */
    uint32_t uptime_ms;           /**< Системний час пристрою (мс) */
} mqtt_telemetry_payload_t;

/**
 * @brief Ініціалізація MQTT клієнта телеметрії.
 * @param client_id Ідентифікатор пристрою.
 * @param broker_ip IP-адреса MQTT-брокера.
 * @param port Порт підключення (наприклад, 1883).
 * @return true у разі успішного налаштування.
 */
bool mqtt_telemetry_init(const char *client_id, const char *broker_ip, uint16_t port);

/**
 * @brief Серіалізація телеметричних даних у формат JSON.
 * @param payload Вказівник на структуру даних.
 * @param buffer Буфер для формування JSON-рядка.
 * @param buffer_size Максимальний розмір бувера.
 * @return Кількість записаних символів або -1 при помилці.
 */
int mqtt_telemetry_serialize_json(const mqtt_telemetry_payload_t *payload, char *buffer, size_t buffer_size);

/**
 * @brief Неблокуюча публікація повідомлення на MQTT-брокер.
 * @param topic MQTT топік публікації.
 * @param json_payload JSON-рядок телеметрії.
 * @param qos Рівень якості обслуговування (0, 1 або 2).
 * @param retain Прапорець збереження останнього повідомлення на брокері.
 * @return true у разі успішної відправки.
 */
bool mqtt_telemetry_publish(const char *topic, const char *json_payload, int qos, bool retain);

/**
 * @brief Зручна функція відправки чергового звіту про водоспоживання.
 * @param metrics Вказівник на поточні метрики давача.
 * @param power_good Прапорець нормального живлення VCC.
 * @return true у разі успішної публікації.
 */
bool mqtt_telemetry_send_flow_report(const water_flow_metrics_t *metrics, bool power_good);

#endif /* MQTT_TELEMETRY_H */
