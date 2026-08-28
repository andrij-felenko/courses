#include "driver/ledc.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define BUZ_GPIO   GPIO_NUM_18
#define BUZ_MODE   LEDC_LOW_SPEED_MODE
#define BUZ_TIMER  LEDC_TIMER_0
#define BUZ_CHAN   LEDC_CHANNEL_0

static int64_t toneOffAt = 0;   // esp_timer_get_time(), коли вимкнути тон (мкс)
static bool    toneOn    = false;

// Меандр жене LEDC: таймер тримає частоту, канал — шпаруватість.
static void buzzerBegin(void)
{
    ledc_timer_config_t timer = {
        .speed_mode      = BUZ_MODE,
        .timer_num       = BUZ_TIMER,
        .duty_resolution = LEDC_TIMER_10_BIT,   // 0…1023
        .freq_hz         = 2000,
        .clk_cfg         = LEDC_AUTO_CLK,
    };
    ESP_ERROR_CHECK(ledc_timer_config(&timer));

    ledc_channel_config_t ch = {
        .gpio_num   = BUZ_GPIO,
        .speed_mode = BUZ_MODE,
        .channel    = BUZ_CHAN,
        .timer_sel  = BUZ_TIMER,
        .duty       = 0,        // старт у тиші
        .hpoint     = 0,
    };
    ESP_ERROR_CHECK(ledc_channel_config(&ch));
}

static void buzzerTone(uint32_t freq)   // ← тутешній відповідник tone()
{
    ledc_set_freq(BUZ_MODE, BUZ_TIMER, freq);
    ledc_set_duty(BUZ_MODE, BUZ_CHAN, 512);   // 512 з 1024 = 50 %, чистий меандр
    ledc_update_duty(BUZ_MODE, BUZ_CHAN);     // без цього duty не поїде в залізо
}

static void buzzerOff(void)             // ← тутешній відповідник noTone()
{
    ledc_set_duty(BUZ_MODE, BUZ_CHAN, 0);
    ledc_update_duty(BUZ_MODE, BUZ_CHAN);
}

void beep(uint32_t freq, uint32_t dur_ms)
{
    buzzerTone(freq);                                           // не чекаємо
    toneOffAt = esp_timer_get_time() + (int64_t)dur_ms * 1000;  // годинник у МКС
    toneOn    = true;
}

void buzzerUpdate(void)   // кликати часто — так само, як у loop()
{
    if (toneOn && esp_timer_get_time() >= toneOffAt) {
        buzzerOff();
        toneOn = false;
    }
}

void app_main(void)
{
    buzzerBegin();
    beep(1000, 200);                    // пікнули 1 кГц на 200 мс
    while (1) {
        buzzerUpdate();                 // ← зумер обслуговується тут, фоном
        vTaskDelay(pdMS_TO_TICKS(2));   // віддали такт іншим задачам FreeRTOS
    }
}
