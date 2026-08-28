#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "driver/uart.h"
#include "esp_intr_alloc.h"

#define EX_UART_NUM UART_NUM_1
static QueueHandle_t uart_event_queue;

/* Завдання нижньої половини (Bottom-Half) */
void uart_event_task(void *pvParameters) {
    uart_event_t event;
    uint8_t dtmp[128];

    for (;;) {
        /* Очікуємо на подію з черги від драйвера переривань */
        if (xQueueReceive(uart_event_queue, (void *)&event, portMAX_DELAY)) {
            switch (event.type) {
                case UART_DATA:
                    /* Зчитуємо дані у потоковому контексті */
                    uart_read_bytes(EX_UART_NUM, dtmp, event.size, portMAX_DELAY);
                    // Важка обробка протоколу...
                    break;
                case UART_BUFFER_FULL:
                case UART_FIFO_OVF:
                    uart_flush_input(EX_UART_NUM);
                    xQueueReset(uart_event_queue);
                    break;
                default:
                    break;
            }
        }
    }
}
