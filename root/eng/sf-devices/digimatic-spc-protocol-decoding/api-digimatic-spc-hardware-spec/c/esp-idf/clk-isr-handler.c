#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"

#define PIN_CLK  GPIO_NUM_4
#define PIN_DATA GPIO_NUM_5

static QueueHandle_t data_queue;
static uint64_t current_packet = 0;
static int bit_count = 0;

static void IRAM_ATTR clk_isr_handler(void* arg) {
    int data_bit = !gpio_get_level(PIN_DATA);
    current_packet |= ((uint64_t)data_bit << bit_count);
    bit_count++;
    
    if (bit_count >= 52) {
        xQueueSendFromISR(data_queue, &current_packet, NULL);
        current_packet = 0;
        bit_count = 0;
    }
}
