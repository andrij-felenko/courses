#include "driver/gpio.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define SHOCK  GPIO_NUM_4     // вивід S давача
#define LED    GPIO_NUM_2     // світлодіод на платі

static const char *TAG = "ky002";

void app_main(void)
{
    gpio_config_t in = {
        .pin_bit_mask = 1ULL << SHOCK,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,     // спокій = 1, струс тягне до 0
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&in));

    gpio_config_t out = {
        .pin_bit_mask = 1ULL << LED,
        .mode         = GPIO_MODE_OUTPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&out));

    int64_t  last_hit = 0;    // мікросекунди останнього зарахованого струсу
    unsigned count    = 0;

    while (1) {
        int level = gpio_get_level(SHOCK);   // 1 = спокій, 0 = контакт замкнувся
        gpio_set_level(LED, level == 0);     // світимо, поки бачимо замикання

        int64_t now = esp_timer_get_time();
        // рахуємо струс, але не частіше ніж раз на 200 мс — гасимо торохтіння пружини
        if (level == 0 && now - last_hit > 200000) {
            last_hit = now;
            ESP_LOGI(TAG, "струс #%u", ++count);
        }
        // щільний цикл; щоб 5 мс не округлилися до нуля, тик FreeRTOS
        // піднімають до 1000 Гц (CONFIG_FREERTOS_HZ), інакше крок буде 10 мс
        vTaskDelay(pdMS_TO_TICKS(5));
    }
}
