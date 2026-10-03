#include "esp_sleep.h"
#include "driver/gpio.h"
#include "esp_log.h"

class PowerManager {
public:
    static void enterAcousticDeepSleep(gpio_num_t trigger_pin) {
        ESP_LOGI("PowerManager", "Ініціалізація сну. Джерело пробудження: GPIO %d", trigger_pin);
        
        // Дозволяємо пробудження мікроконтролера при зміні стану компаратора
        esp_sleep_enable_ext0_wakeup(trigger_pin, 1);
        
        ESP_LOGI("PowerManager", "Вхід у режим Deep Sleep.");
        esp_deep_sleep_start();
    }
};
