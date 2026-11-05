#include <stdint.h>
#include <stdbool.h>
#include "driver/gpio.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"

typedef struct {
    uint64_t pps_uptime_us; // Uptime моменту фронту PPS
} pps_event_t;

static QueueHandle_t g_pps_queue = NULL;

// ISR обробник апаратного переривання виводу PPS від GNSS
static void IRAM_ATTR pps_gpio_isr_handler(void* arg) {
    pps_event_t evt;
    evt.pps_uptime_us = esp_timer_get_time(); // Миттєве фіксування тика
    
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    xQueueSendFromISR(g_pps_queue, &evt, &xHigherPriorityTaskWoken);
    if (xHigherPriorityTaskWoken) {
        portYIELD_FROM_ISR();
    }
}

// Фонова задача узгодження PPS та NMEA часових міток
void pps_sync_task(void* arg) {
    pps_event_t evt;
    while (1) {
        if (xQueueReceive(g_pps_queue, &evt, portMAX_DELAY)) {
            // Очікування arrival NMEA дати для цієї секунди
            uint64_t gnss_utc_sec = 1700000000ULL; // Отримані дані з UART NMEA
            uint64_t target_wall_us = gnss_utc_sec * 1000000ULL;
            
            // Розрахунок нового точного зсуву
            int64_t new_offset = (int64_t)target_wall_us - (int64_t)evt.pps_uptime_us;
            
            // Застосування зсуву до підсистеми часу
            // set_system_time_offset(new_offset);
        }
    }
}

void pps_driver_init(gpio_num_t pps_pin) {
    g_pps_queue = xQueueCreate(10, sizeof(pps_event_t));
    
    gpio_config_t io_conf = {
        .intr_type = GPIO_INTR_POSEDGE,
        .pin_bit_mask = (1ULL << pps_pin),
        .mode = GPIO_MODE_INPUT,
        .pull_down_en = GPIO_PULLDOWN_ENABLE
    };
    gpio_config(&io_conf);
    
    gpio_install_isr_service(0);
    gpio_isr_handler_add(pps_pin, pps_gpio_isr_handler, NULL);
}
