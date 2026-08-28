#include <stdint.h>
#include <stdbool.h>
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

#define BUF_SIZE 1024
static uint8_t buf_a[BUF_SIZE] __attribute__((aligned(32)));
static uint8_t buf_b[BUF_SIZE] __attribute__((aligned(32)));

static volatile bool use_buf_a = false;   /* який буфер ЗАРАЗ читає ядро */
static SemaphoreHandle_t sem_ready;

/* Переривання завершення DMA: активний буфер дописано */
void IRAM_ATTR dma_completion_isr(void *arg) {
    BaseType_t woken = pdFALSE;
    use_buf_a = !use_buf_a;                /* атомарний обмін ролей */
    xSemaphoreGiveFromISR(sem_ready, &woken);
    portYIELD_FROM_ISR(woken);            /* прокинути задачу негайно */
}

/* Задача, що обробляє готовий буфер */
void process_task(void *pv) {
    while (1) {
        xSemaphoreTake(sem_ready, portMAX_DELAY);   /* чекати «готово» */
        uint8_t *ready = use_buf_a ? buf_a : buf_b; /* свіжо дописаний */
        /* DMA саме зараз пише в ІНШИЙ буфер — ready недоторканний */
        process_block(ready, BUF_SIZE);
    }
}
