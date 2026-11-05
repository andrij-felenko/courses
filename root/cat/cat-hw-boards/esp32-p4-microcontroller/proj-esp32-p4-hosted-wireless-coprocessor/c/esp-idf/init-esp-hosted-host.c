#include "esp_hosted_api.h"
#include "esp_netif.h"
#include "esp_wifi.h"
#include "esp_log.h"

static const char *TAG = "HOST_INIT";

esp_err_t init_esp_hosted_host(void) {
    // Ініціалізація мережевого стека LwIP
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    // Конфігурація та запуск хост-драйвера ESP-HOSTED
    esp_hosted_config_t hosted_cfg = {
        .transport = ESP_HOSTED_TRANSPORT_SDIO,
        .clock_freq_hz = 50 * 1000 * 1000,
        .gpio_data_ready = GPIO_NUM_4,
        .gpio_handshake = GPIO_NUM_5,
    };
    
    esp_err_t ret = esp_hosted_init(&hosted_cfg);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації ESP-HOSTED: %s", esp_err_to_name(ret));
        return ret;
    }

    // Створення віртуального Wi-Fi адаптера LwIP
    esp_netif_create_default_wifi_sta();
    ESP_LOGI(TAG, "Бездротовий стек ESP-HOSTED успішно підключено");
    return ESP_OK;
}
