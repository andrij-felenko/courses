#include "driver/gpio.h"
#include "esp_log.h"
#include "esp_err.h"

class SipPinChecker {
private:
    static constexpr const char* TAG = "SipPinChecker";

public:
    static bool validate_pin(gpio_num_t pin) {
        // У SiP-корпусі ESP32-S3-MINI-1 лінії GPIO33-GPIO37 розведені на кристал Flash
        if (pin >= GPIO_NUM_33 && pin <= GPIO_NUM_37) {
            ESP_LOGW(TAG, "Спроба доступу до приватного виводу SiP: GPIO%d", static_cast<int>(pin));
            return false;
        }
        return true;
    }
};
