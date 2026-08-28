#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"

typedef struct {
    uint32_t length;
    uint8_t  payload[64]; /* Статичний фіксований буфер під переривання */
} isr_packet_t;

static QueueHandle_t isr_packet_queue = NULL;

/* Обробник апаратного переривання: жодних викликів malloc! */
void IRAM_ATTR uart_rx_isr_handler(void)
{
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    isr_packet_t packet;

    packet.length = 32; /* Зчитування з регістру FIFO */
    /* ... заповнення packet.payload ... */

    /* Передаємо фіксовану структуру через чергу без динамічної алокації */
    xQueueSendFromISR(isr_packet_queue, &packet, &xHigherPriorityTaskWoken);

    if (xHigherPriorityTaskWoken == pdTRUE) {
        portYIELD_FROM_ISR();
    }
}
