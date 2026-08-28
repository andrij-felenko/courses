#include "driver/ledc.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// дві обгортки — уся платформозалежність рушія
static uint32_t millis(void) { return (uint32_t)(esp_timer_get_time() / 1000); }

static void ledcWrite(uint8_t ch, uint32_t duty) {
    ledc_set_duty(LEDC_LOW_SPEED_MODE, (ledc_channel_t)ch, duty);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, (ledc_channel_t)ch);   // duty бере силу тут
}

static void animTask(void *arg) {
    for (;;) {
        uint32_t now = millis();
        animTick(now);                     // посунути всі ефекти
        queueTick();                       // просунути всі черги
        vTaskDelay(pdMS_TO_TICKS(10));     // ~100 кадрів/с, решта часу — іншим задачам
    }
}

void app_main(void) {
    ledc_timer_config_t t = { .speed_mode = LEDC_LOW_SPEED_MODE,
                              .duty_resolution = LEDC_TIMER_12_BIT,  // ті самі 12 біт
                              .timer_num = LEDC_TIMER_0, .freq_hz = 5000,
                              .clk_cfg = LEDC_AUTO_CLK };
    ESP_ERROR_CHECK(ledc_timer_config(&t));
    for (int ch = 0; ch < 2; ch++) {                   // канал 0 → GPIO2, канал 1 → GPIO4
        ledc_channel_config_t c = { .gpio_num = (ch == 0) ? 2 : 4,
                                    .speed_mode = LEDC_LOW_SPEED_MODE,
                                    .channel = (ledc_channel_t)ch,
                                    .timer_sel = LEDC_TIMER_0, .duty = 0, .hpoint = 0 };
        ESP_ERROR_CHECK(ledc_channel_config(&c));
    }
    buildLUT();
    buildShapeTables();

    animStart(0, ANIM_PINGPONG, shapeBreathe, 4000, false);
    queueStart(0, /*канал=*/1, /*invert=*/false, alarmThenCalm, 2);
    xTaskCreate(animTask, "anim", 4096, NULL, 5, NULL);
}
