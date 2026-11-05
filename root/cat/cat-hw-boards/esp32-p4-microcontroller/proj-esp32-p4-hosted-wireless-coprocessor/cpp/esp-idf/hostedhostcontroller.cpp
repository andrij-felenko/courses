#include "esp_hosted_api.h"
#include "esp_netif.h"
#include "esp_wifi.h"
#include "esp_log.h"

class HostedHostController {
public:
    static esp_err_t initialize() {
        ESP_ERROR_CHECK(esp_netif_init());
        ESP_ERROR_CHECK(esp_event_loop_create_default());

        esp_hosted_config_t hosted_cfg = {};
        hosted_cfg.transport = ESP_HOSTED_TRANSPORT_SDIO;
        hosted_cfg.clock_freq_hz = 50 * 1000 * 1000;
        hosted_cfg.gpio_data_ready = GPIO_NUM_4;
        hosted_cfg.gpio_handshake = GPIO_NUM_5;

        esp_err_t ret = esp_hosted_init(&hosted_cfg);
        if (ret == ESP_OK) {
            esp_netif_create_default_wifi_sta();
            ESP_LOGI("HOST_CPP", "Хост-драйвер успішно ініціалізовано");
        }
        return ret;
    }
};
