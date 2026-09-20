#include "mqtt_app.h"
#include "esp_log.h"
#include <string.h>

static const char *TAG = "MQTT_APP";

static esp_mqtt_client_handle_t s_mqtt_client = NULL;
static relay_handle_t *s_relay_handle = NULL;

esp_err_t mqtt_app_publish_status(relay_state_t state)
{
    if (s_mqtt_client == NULL) {
        return ESP_ERR_INVALID_STATE;
    }

    const char *payload = (state == RELAY_STATE_ON) ? "ON" : "OFF";
    int msg_id = esp_mqtt_client_publish(s_mqtt_client, MQTT_TOPIC_STATUS, payload, 0, 1, 1);
    if (msg_id >= 0) {
        ESP_LOGI(TAG, "Публікація статусу реле у топік '%s': %s (msg_id=%d)",
                 MQTT_TOPIC_STATUS, payload, msg_id);
        return ESP_OK;
    } else {
        ESP_LOGE(TAG, "Помилка публікації статусу у MQTT");
        return ESP_FAIL;
    }
}

/**
 * @brief Обробник подій MQTT-клієнта.
 */
static void mqtt_event_handler(void *handler_args, esp_event_base_t base, int32_t event_id, void *event_data)
{
    esp_mqtt_event_handle_t event = (esp_mqtt_event_handle_t)event_data;

    switch (event->event_id) {
    case MQTT_EVENT_CONNECTED:
        ESP_LOGI(TAG, "З'єднання з MQTT-брокером встановлено успішно");
        /* Підписка на топік керуючих команд із QoS 1 */
        esp_mqtt_client_subscribe(s_mqtt_client, MQTT_TOPIC_COMMAND, 1);
        ESP_LOGI(TAG, "Підписано на топік команд: %s", MQTT_TOPIC_COMMAND);

        /* Публікація поточного стану при підключенні */
        if (s_relay_handle != NULL) {
            relay_state_t current = relay_driver_get_state(s_relay_handle);
            mqtt_app_publish_status(current);
        }
        break;

    case MQTT_EVENT_DISCONNECTED:
        ESP_LOGW(TAG, "Втрачено з'єднання з MQTT-брокером. Очікування автоматичного перепідключення...");
        break;

    case MQTT_EVENT_SUBSCRIBED:
        ESP_LOGI(TAG, "Підтвердження підписки (msg_id=%d)", event->msg_id);
        break;

    case MQTT_EVENT_DATA: {
        ESP_LOGI(TAG, "Отримано MQTT-повідомлення у топіку: %.*s", event->topic_len, event->topic);

        /* Витягуємо вміст команди */
        char payload_buf[32] = {0};
        int len = (event->data_len < sizeof(payload_buf) - 1) ? event->data_len : (sizeof(payload_buf) - 1);
        memcpy(payload_buf, event->data, len);
        payload_buf[len] = '\0';

        ESP_LOGI(TAG, "Команда: %s", payload_buf);

        if (s_relay_handle != NULL) {
            if (strcasecmp(payload_buf, "ON") == 0 || strcmp(payload_buf, "1") == 0 || strcasecmp(payload_buf, "TRUE") == 0) {
                relay_driver_set_state(s_relay_handle, RELAY_STATE_ON);
                mqtt_app_publish_status(RELAY_STATE_ON);
            } else if (strcasecmp(payload_buf, "OFF") == 0 || strcmp(payload_buf, "0") == 0 || strcasecmp(payload_buf, "FALSE") == 0) {
                relay_driver_set_state(s_relay_handle, RELAY_STATE_OFF);
                mqtt_app_publish_status(RELAY_STATE_OFF);
            } else if (strcasecmp(payload_buf, "TOGGLE") == 0) {
                relay_driver_toggle(s_relay_handle);
                relay_state_t new_st = relay_driver_get_state(s_relay_handle);
                mqtt_app_publish_status(new_st);
            } else {
                ESP_LOGW(TAG, "Отримано невідому команду MQTT: %s", payload_buf);
            }
        }
        break;
    }

    case MQTT_EVENT_ERROR:
        ESP_LOGE(TAG, "Виникла помилка у MQTT-клієнті");
        break;

    default:
        break;
    }
}

esp_err_t mqtt_app_start(const mqtt_app_config_t *config)
{
    if (config == NULL || strlen(config->broker_uri) == 0 || config->relay_handle == NULL) {
        ESP_LOGE(TAG, "Недійсні параметри конфігурації MQTT");
        return ESP_ERR_INVALID_ARG;
    }

    s_relay_handle = config->relay_handle;

    esp_mqtt_client_config_t mqtt_cfg = {
        .broker = {
            .address = {
                .uri = config->broker_uri,
            },
        },
        .credentials = {
            .client_id = (strlen(config->client_id) > 0) ? config->client_id : "ESP01S_Relay_Client",
            .username = (strlen(config->username) > 0) ? config->username : NULL,
            .authentication = {
                .password = (strlen(config->password) > 0) ? config->password : NULL,
            },
        },
    };

    s_mqtt_client = esp_mqtt_client_init(&mqtt_cfg);
    if (s_mqtt_client == NULL) {
        ESP_LOGE(TAG, "Не вдалося ініціалізувати MQTT-клієнт");
        return ESP_FAIL;
    }

    ESP_ERROR_CHECK(esp_mqtt_client_register_event(s_mqtt_client, ESP_EVENT_ANY_ID, mqtt_event_handler, NULL));
    ESP_ERROR_CHECK(esp_mqtt_client_start(s_mqtt_client));

    ESP_LOGI(TAG, "MQTT-клієнт запущено (URI: %s)", config->broker_uri);
    return ESP_OK;
}

esp_err_t mqtt_app_stop(void)
{
    if (s_mqtt_client != NULL) {
        esp_mqtt_client_stop(s_mqtt_client);
        esp_mqtt_client_destroy(s_mqtt_client);
        s_mqtt_client = NULL;
        s_relay_handle = NULL;
        ESP_LOGI(TAG, "MQTT-клієнт зупинено");
    }
    return ESP_OK;
}
