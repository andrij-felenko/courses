#include "driver/ledc.h"
#include "driver/gpio.h"
#include "esp_system.h"
#include "esp_log.h"
static const char *TAG = "safe";

#define GPIO_HEATER_RELAY  GPIO_NUM_5    // active HIGH: HIGH = гріє
#define GPIO_VALVE_CLOSE   GPIO_NUM_18   // active HIGH: HIGH = закрити н/з клапан
#define GPIO_FAULT_LED     GPIO_NUM_19   // active HIGH: індикатор аварії
#define MOTOR_LEDC_CHANNEL LEDC_CHANNEL_0

#define FAULT_THRESHOLD    5             // патологічних збоїв за "вікно"

// Лічильник у RTC-пам'яті: переживає reset, але не повне знеструмлення.
RTC_NOINIT_ATTR static uint32_t s_fault_cnt;

// 1) Безпечний стан — найперша дія при будь-якій критичній помилці.
void enter_safe_state(void) {
    ESP_LOGE(TAG, "ENTER SAFE STATE");                 // лог — ПІСЛЯ гасіння

    ledc_set_duty(LEDC_LOW_SPEED_MODE, MOTOR_LEDC_CHANNEL, 0);  // мотор: duty 0
    ledc_update_duty(LEDC_LOW_SPEED_MODE, MOTOR_LEDC_CHANNEL);
    ledc_stop(LEDC_LOW_SPEED_MODE, MOTOR_LEDC_CHANNEL, 0);      // idle level = 0

    gpio_set_level(GPIO_HEATER_RELAY, 0);   // нагрівач: реле розімкнуто
    gpio_set_level(GPIO_VALVE_CLOSE, 1);    // н/з клапан: закрити
    gpio_set_level(GPIO_FAULT_LED, 1);      // індикатор аварії
    // Wi-Fi/BLE стек НЕ зупиняємо — він потрібен для діагностики й OTA.
}

// 2) На старті: вирішити, чи піднімати safe mode, чи нормальний режим.
void startup(void) {
    enter_safe_state();                     // виходи безпечні ще до рішення

    esp_reset_reason_t r = esp_reset_reason();
    if (r == ESP_RST_POWERON) s_fault_cnt = 0;          // людина увімкнула — чисто
    else if (r == ESP_RST_PANIC || r == ESP_RST_TASK_WDT)
        s_fault_cnt++;                                  // патологічний збій — рахувати

    if (s_fault_cnt >= FAULT_THRESHOLD) {
        ESP_LOGE(TAG, "fault loop (cnt=%lu) -> SAFE MODE", s_fault_cnt);
        start_minimal_services();           // лише зв'язок + OTA + індикація
        return;                             // основну функцію НЕ запускаємо
    }

    start_full_application();               // звичайний режим
}
