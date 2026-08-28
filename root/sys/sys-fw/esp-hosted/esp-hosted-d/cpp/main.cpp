#include "esp_hosted.h"     // транспорт до веденого
#include "esp_wifi.h"       // той самий звичний Wi-Fi API
#include "esp_netif.h"
#include "esp_event.h"

void app_main(void)
{
    // 0) службове: цикл подій і мережевий інтерфейс — як на звичайному ESP32
    esp_event_loop_create_default();
    esp_netif_init();
    esp_netif_create_default_wifi_sta();

    // 1) ЄДИНИЙ новий крок: підняти лінію до веденого (тут — SDIO).
    //    Яка шина й ніжки — задано в конфігурації прошивки.
    esp_hosted_init();          // рукостискання з ESP32-C6 по транспорту

    // 2) далі — звичайний ESP-IDF Wi-Fi: виклики ті самі, що й на одночиповому ESP32,
    //    але Wi-Fi Remote тихо переадресовує їх через лінію до веденого
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    esp_wifi_init(&cfg);

    wifi_config_t wc = {
        .sta = { .ssid = "MyNetwork", .password = "secret123" },
    };
    esp_wifi_set_mode(WIFI_MODE_STA);
    esp_wifi_set_config(WIFI_IF_STA, &wc);
    esp_wifi_start();
    esp_wifi_connect();         // команда йде до C6 — радіо крутить ВІН

    // 3) звідси й далі ведучий має повноцінний мережевий інтерфейс:
    //    приходить подія IP_EVENT_STA_GOT_IP, відкриваються сокети, HTTP тощо
}
