#include "driver/gpio.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_PIR  GPIO_NUM_33
#define PIN_LED  GPIO_NUM_2

#define WARMUP_MS   60000U    // прогрів
#define LOCKOUT_MS  3000U     // не приймати нову подію раніше, ніж мине стільки

static const char *TAG = "pir";
static uint32_t counter;      // скільки подій нарахували

static inline uint32_t now_ms(void) { return (uint32_t)(esp_timer_get_time() / 1000); }

static void alarm_event(void) {
    counter++;
    ESP_LOGW(TAG, "ТРИВОГА, подія #%u", (unsigned)counter);
    // тут: надіслати пакет по Wi-Fi, зробити кадр, увімкнути сирену на мить тощо
    gpio_set_level(PIN_LED, 1);
    vTaskDelay(pdMS_TO_TICKS(100));   // коротке блимання — для наочності
    gpio_set_level(PIN_LED, 0);
}

static void pir_task(void *arg) {
    uint32_t t_boot = now_ms(), t_last_event = 0;
    int pir_prev = gpio_get_level(PIN_PIR);   // попередній рівень OUT (для виявлення фронту)

    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(20));        // грубий дебаунс краю
        uint32_t now = now_ms();
        if (now - t_boot < WARMUP_MS) continue;          // гасіння прогріву

        int pir = gpio_get_level(PIN_PIR);
        // Виявлення переднього фронту: було 0, стало 1 — це нова поява руху.
        if (pir && !pir_prev && now - t_last_event >= LOCKOUT_MS) {
            t_last_event = now;
            alarm_event();
        }
        pir_prev = pir;
    }
}

void app_main(void) {
    gpio_config_t in = { .pin_bit_mask = 1ULL << PIN_PIR, .mode = GPIO_MODE_INPUT,
                         .pull_up_en = GPIO_PULLUP_DISABLE, .pull_down_en = GPIO_PULLDOWN_DISABLE,
                         .intr_type = GPIO_INTR_DISABLE };
    ESP_ERROR_CHECK(gpio_config(&in));
    gpio_reset_pin(PIN_LED);
    ESP_ERROR_CHECK(gpio_set_direction(PIN_LED, GPIO_MODE_OUTPUT));
    xTaskCreate(pir_task, "pir", 3072, NULL, 5, NULL);
}
