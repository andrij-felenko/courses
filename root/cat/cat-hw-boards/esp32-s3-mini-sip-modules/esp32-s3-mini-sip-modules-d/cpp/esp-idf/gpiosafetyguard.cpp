#include "driver/gpio.h"
#include "esp_log.h"
#include "esp_err.h"

class GpioSafetyGuard {
private:
    static constexpr const char* TAG = "GpioSafetyGuard";

public:
    static bool is_safe_for_output(gpio_num_t pin) {
        // Лінії internal Flash та GPIO46 заборонені для виходу
        if ((pin >= GPIO_NUM_33 && pin <= GPIO_NUM_37) || pin == GPIO_NUM_46) {
            ESP_LOGE(TAG, "Вивід GPIO%d недоступний для вихідних сигналів", static_cast<int>(pin));
            return false;
        }
        
        if (pin == GPIO_NUM_0 || pin == GPIO_NUM_45) {
            ESP_LOGW(TAG, "Призначення виходу на strapping-вивід GPIO%d вимагає ізоляції", static_cast<int>(pin));
        }
        
        return true;
    }
};
