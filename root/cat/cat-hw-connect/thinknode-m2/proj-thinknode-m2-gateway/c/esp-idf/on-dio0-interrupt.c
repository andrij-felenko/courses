#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"

QueueHandle_t packet_queue;
volatile bool packet_received = false;

void IRAM_ATTR on_dio0_interrupt(void* arg) {
    packet_received = true;
}

void app_main() {
    packet_queue = xQueueCreate(10, 256);
    
    while (1) {
        // 1. Швидко забираємо дані з радіомодуля
        if (packet_received) {
            packet_received = false;
            uint8_t data[256];
            read_lora_buffer(data);
            xQueueSend(packet_queue, &data, 0);
        }

        // 2. Повільно відправляємо через Wi-Fi
        uint8_t data_to_send[256];
        if (xQueueReceive(packet_queue, &data_to_send, 0)) {
            send_to_server(data_to_send, 256);
        }
        
        vTaskDelay(10 / portTICK_PERIOD_MS);
    }
}
