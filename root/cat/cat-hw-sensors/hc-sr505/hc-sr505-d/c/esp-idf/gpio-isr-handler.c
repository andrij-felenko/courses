#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "esp_sleep.h"
#include "esp_log.h"

#define PIR_INPUT_PIN GPIO_NUM_4
static const char *TAG = "HC-SR505";

static void IRAM_ATTR gpio_isr_handler(void *arg) {
    // Обробник переривання: фіксація виявленого руху
}

void app_main(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << PIR_INPUT_PIN),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,
        .intr_type = GPIO_INTR_POSEDGE
    };
    gpio_config(&io_conf);

    // Активація пробудження від високого рівня на піні GPIO4
    esp_deep_sleep_enable_gpio_wakeup(1ULL << PIR_INPUT_PIN, ESP_GPIO_WAKEUP_GPIO_HIGH);
    
    ESP_LOGI(TAG, "Перехід у режим глибокого сну до фіксації руху...");
    esp_deep_sleep_start();
}
