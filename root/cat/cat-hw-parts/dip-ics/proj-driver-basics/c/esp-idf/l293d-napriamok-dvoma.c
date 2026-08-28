// L293D, перший міст: мотор між OUT1 (вивід 3) і OUT2 (вивід 6).
// EN1 (вивід 1) — на GPIO з апаратним ШІМ (в ESP32 це будь-який вивід через LEDC).
// IN1 (вивід 2) і IN2 (вивід 7) — на будь-які цифрові GPIO.
// Vss (вивід 16) = 5V логіки; Vs (вивід 8) = живлення мотора; GND (4,5,12,13) спільна з МК.
#include "driver/gpio.h"
#include "driver/ledc.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define EN1  GPIO_NUM_18          // будь-який GPIO: ШІМ туди заводить LEDC
#define IN1  GPIO_NUM_19
#define IN2  GPIO_NUM_21
#define CH   LEDC_CHANNEL_0

static void set_speed(uint8_t speed) {          // speed 0..255 — глибина ШІМ
    ledc_set_duty(LEDC_LOW_SPEED_MODE, CH, speed);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, CH);
}

static void forward(uint8_t speed) {
    gpio_set_level(IN1, 1);
    gpio_set_level(IN2, 0);
    set_speed(speed);                            // ШІМ на enable = оберти
}

static void backward(uint8_t speed) {
    gpio_set_level(IN1, 0);
    gpio_set_level(IN2, 1);
    set_speed(speed);
}

static void brake(void) {                        // динамічне гальмо: enable є, входи однакові
    gpio_set_level(IN1, 1);
    gpio_set_level(IN2, 1);
    set_speed(255);                              // міст увімкнено на повну, обмотка закорочена
}

static void coast(void) { set_speed(0); }        // вільний хід: enable знято

void app_main(void) {
    gpio_config_t io = { .pin_bit_mask = (1ULL << IN1) | (1ULL << IN2),
                         .mode = GPIO_MODE_OUTPUT };
    gpio_config(&io);

    ledc_timer_config_t t = {                    // таймер задає частоту й розрядність ШІМ
        .speed_mode = LEDC_LOW_SPEED_MODE, .timer_num = LEDC_TIMER_0,
        .duty_resolution = LEDC_TIMER_8_BIT,     // 8 біт → duty так само 0..255
        .freq_hz = 1000, .clk_cfg = LEDC_AUTO_CLK,
    };
    ledc_timer_config(&t);
    ledc_channel_config_t c = {                  // канал прив'язує таймер до ноги EN1
        .gpio_num = EN1, .speed_mode = LEDC_LOW_SPEED_MODE, .channel = CH,
        .timer_sel = LEDC_TIMER_0, .duty = 0, .hpoint = 0,
    };
    ledc_channel_config(&c);

    while (1) {
        forward(180);   vTaskDelay(pdMS_TO_TICKS(1500));   // вперед на ~70% обертів
        coast();        vTaskDelay(pdMS_TO_TICKS(500));    // відпустили — котиться
        backward(120);  vTaskDelay(pdMS_TO_TICKS(1500));   // назад повільніше
        brake();        vTaskDelay(pdMS_TO_TICKS(500));    // різко спинили
    }
}
