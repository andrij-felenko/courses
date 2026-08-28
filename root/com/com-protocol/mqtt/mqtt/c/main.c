#include "mqtt_client.h"   // клієнт ESP-MQTT з ESP-IDF
#include "esp_log.h"
#include <string.h>

static const char *TAG = "mqtt";

// Один обробник на всі події клієнта: з'єднання, прихід даних тощо.
static void mqtt_event_handler(void *args, esp_event_base_t base,
                               int32_t event_id, void *event_data)
{
    esp_mqtt_event_handle_t e = event_data;
    esp_mqtt_client_handle_t client = e->client;

    switch ((esp_mqtt_event_id_t)event_id) {

    case MQTT_EVENT_CONNECTED:               // брокер прийняв з'єднання
        // 1) підписуємось на топік команд (QoS 1)
        esp_mqtt_client_subscribe(client, "home/room/cmd", 1);

        // 2) публікуємо показання: топік, текст, довжина(0 = порахувати),
        //    QoS = 1, retain = 1 (брокер запам'ятає як останнє значення)
        esp_mqtt_client_publish(client, "home/room/temp", "23.4", 0, 1, 1);
        ESP_LOGI(TAG, "під'єднано: підписались і опублікували");
        break;

    case MQTT_EVENT_DATA:                    // прийшло повідомлення на наш топік
        // 3) обробка приходу даних: топік і тіло — не C-рядки, тож по довжині
        ESP_LOGI(TAG, "топік %.*s = %.*s",
                 e->topic_len, e->topic,
                 e->data_len,  e->data);
        break;

    case MQTT_EVENT_DISCONNECTED:
        ESP_LOGW(TAG, "з'єднання з брокером втрачено");
        break;

    default:
        break;
    }
}

void mqtt_start(void)
{
    // адреса брокера; "останню волю" віддамо тут же, у конфігурації
    esp_mqtt_client_config_t cfg = {
        .broker.address.uri = "mqtt://192.168.1.10",
        .session.last_will.topic   = "home/room/status",
        .session.last_will.msg     = "offline",   // заповіт: брокер опублікує,
        .session.last_will.qos     = 1,           // якщо ми зникнемо раптово
        .session.last_will.retain  = 1,
        .session.keepalive         = 60,          // озиватись бодай раз на 60 с
    };

    esp_mqtt_client_handle_t client = esp_mqtt_client_init(&cfg);
    // підписуємо наш обробник на всі події клієнта
    esp_mqtt_client_register_event(client, ESP_EVENT_ANY_ID,
                                   mqtt_event_handler, NULL);
    esp_mqtt_client_start(client);   // під'єднатись і крутити обмін у фоні
}
