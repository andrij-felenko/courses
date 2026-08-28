#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"

static QueueHandle_t q;                        // черга замість власного кільця

static void IRAM_ATTR on_byte(void *arg) {     // верхня половина
    uint8_t b = read_byte();                   // лише читання регістра
    BaseType_t woken = pdFALSE;
    xQueueSendFromISR(q, &b, &woken);          // черга повна — байт відкидається
    if (woken) portYIELD_FROM_ISR();           // розбудили задачу — віддати їй CPU
}

static void parser_task(void *arg) {           // нижня половина
    uint8_t b;
    while (xQueueReceive(q, &b, portMAX_DELAY) == pdTRUE)
        parse(b);                              // розбір, друк, математика — без поспіху
}

void app_main(void) {
    q = xQueueCreate(64, sizeof(uint8_t));     // 64 байти місткості
    xTaskCreate(parser_task, "parser", 4096, NULL, 5, NULL);
}
