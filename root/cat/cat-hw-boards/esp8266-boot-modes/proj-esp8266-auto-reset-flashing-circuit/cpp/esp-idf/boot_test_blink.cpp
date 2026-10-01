// Тестування автономного завантаження ESP8266 в середовищі ESP-IDF (C++)
// Клас BlinkIndicator забезпечує безпечне управління GPIO та діагностику у FreeRTOS

#include <cstdio>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "esp_system.h"
#include "esp_log.h"

static const char *TAG = "BOOT_VERIFY";

// ООП-клас для управління індикаторним світлодіодом під час тестування завантаження
class BlinkIndicator {
public:
    explicit BlinkIndicator(gpio_num_t pin, bool inverted = true)
        : pin_(pin), inverted_(inverted), state_(false), counter_(0) {}

    ~BlinkIndicator() = default;

    // Ініціалізація виводу GPIO та виведення початкового діагностичного логу
    esp_err_t init() {
        gpio_config_t io_conf = {};
        io_conf.intr_type = GPIO_INTR_DISABLE;
        io_conf.mode = GPIO_MODE_OUTPUT;
        io_conf.pin_bit_mask = (1ULL << pin_);
        io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
        io_conf.pull_up_en = GPIO_PULLUP_ENABLE;

        esp_err_t err = gpio_config(&io_conf);
        if (err != ESP_OK) {
            ESP_LOGE(TAG, "Помилка конфігурації GPIO %d: 0x%x", pin_, err);
            return err;
        }

        set_level(false);
        ESP_LOGI(TAG, "Ініціалізовано BlinkIndicator на GPIO %d (інверсія: %s)",
                 pin_, inverted_ ? "ТАК" : "НІ");
        return ESP_OK;
    }

    // Перемикання стану світлодіода
    void toggle() {
        state_ = !state_;
        counter_++;
        set_level(state_);
        ESP_LOGI(TAG, "[CYCLE #%u] Світлодіод %s",
                 (unsigned int)counter_, state_ ? "УВІМКНЕНО" : "ВИМКНЕНО");
    }

    [[nodiscard]] uint32_t get_counter() const noexcept { return counter_; }

private:
    void set_level(bool active) {
        bool level = inverted_ ? !active : active;
        gpio_set_level(pin_, level ? 1 : 0);
    }

    gpio_num_t pin_;
    bool inverted_;
    bool state_;
    uint32_t counter_;
};

extern "C" void app_main(void)
{
    ESP_LOGI(TAG, "=========================================");
    ESP_LOGI(TAG, "ESP8266 ESP-IDF Boot Verification Test");
    ESP_LOGI(TAG, "Перевірка переходу чипа в режим SPI Flash Boot");
    ESP_LOGI(TAG, "=========================================");

    // Отримання системної інформації
    esp_chip_info_t chip_info;
    esp_chip_info(&chip_info);
    ESP_LOGI(TAG, "Кількість ядер CPU: %d, ревізія чипа: %d", chip_info.cores, chip_info.revision);
    ESP_LOGI(TAG, "Вільна операційна пам'ять Heap: %u байт", (unsigned int)esp_get_free_heap_size());

    // Створення об'єкта миготіння на GPIO2 (вбудований LED модулів ESP-12)
    BlinkIndicator indicator(GPIO_NUM_2, true);

    if (indicator.init() != ESP_OK) {
        ESP_LOGE(TAG, "Критична помилка ініціалізації індикатора завантаження");
        return;
    }

    ESP_LOGI(TAG, "Автономний запуск прошивки з Flash-пам'яті підтверджено!");

    // Головний цикл миготіння у задачі FreeRTOS
    while (true) {
        indicator.toggle();
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}
