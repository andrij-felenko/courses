/* esp_supervisor.c — C-реалізація */
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "driver/gpio.h"
#include "esp_log.h"

#define WDI_GPIO_PIN        GPIO_NUM_18
#define PFO_INTR_PIN        GPIO_NUM_19
#define TASK_SENSOR_BIT     BIT0
#define TASK_COMM_BIT       BIT1
#define ALL_TASKS_BITS      (TASK_SENSOR_BIT | TASK_COMM_BIT)

static EventGroupHandle_t s_watchdog_event_group;
static const char *TAG = "SUPERVISOR";

static void IRAM_ATTR pfo_isr_handler(void* arg) {
    /* Раннє вимкнення радіотракту Wi-Fi/BLE при падінні живлення */
    gpio_set_level(GPIO_NUM_21, 0);
}

void app_supervisor_task(void *pvParameters) {
    s_watchdog_event_group = xEventGroupCreate();
    gpio_set_direction(WDI_GPIO_PIN, GPIO_MODE_OUTPUT);
    
    int pin_level = 0;
    TickType_t last_wake_time = xTaskGetTickCount();
    const TickType_t service_period = pdMS_TO_TICKS(50); /* 50 мс — центр вікна */

    while (1) {
        vTaskDelayUntil(&last_wake_time, service_period);

        EventBits_t bits = xEventGroupWaitBits(
            s_watchdog_event_group,
            ALL_TASKS_BITS,
            pdTRUE,  /* Очистити прапорці після читання */
            pdTRUE,  /* Чекати ВСІ прапорці */
            0        /* Без блокування */
        );

        if ((bits & ALL_TASKS_BITS) == ALL_TASKS_BITS) {
            pin_level = !pin_level;
            gpio_set_level(WDI_GPIO_PIN, pin_level);
        } else {
            ESP_LOGE(TAG, "Watchdog: окремі задачі пропустили ітерацію!");
        }
    }
}
