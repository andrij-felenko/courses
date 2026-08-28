#include "stm32f4xx_hal.h"

/* Прапорець готовності — volatile: колбек виконується в ISR */
static volatile bool dma_done;
static DMA_HandleTypeDef hdma;

static void dma_cb(DMA_HandleTypeDef *h) { dma_done = true; }

/* Одноразове налаштування каналу (виконується один раз при старті) */
void dma_init(void) {
    __HAL_RCC_DMA2_CLK_ENABLE();          /* M2M вміє лише DMA2 на F4 */
    hdma.Instance                 = DMA2_Stream0;
    hdma.Init.Channel             = DMA_CHANNEL_0;
    hdma.Init.Direction           = DMA_MEMORY_TO_MEMORY;
    hdma.Init.PeriphInc           = DMA_PINC_ENABLE;   /* джерело теж інкрементуємо */
    hdma.Init.MemInc              = DMA_MINC_ENABLE;
    hdma.Init.PeriphDataAlignment = DMA_PDATAALIGN_WORD;
    hdma.Init.MemDataAlignment    = DMA_MDATAALIGN_WORD;
    hdma.Init.Mode                = DMA_NORMAL;
    hdma.Init.Priority            = DMA_PRIORITY_HIGH;
    hdma.Init.FIFOMode            = DMA_FIFOMODE_ENABLE;  /* у M2M FIFO обов'язкове */
    hdma.Init.FIFOThreshold       = DMA_FIFO_THRESHOLD_FULL;
    HAL_DMA_Init(&hdma);
    HAL_DMA_RegisterCallback(&hdma, HAL_DMA_XFER_CPLT_CB_ID, dma_cb);
    HAL_NVIC_EnableIRQ(DMA2_Stream0_IRQn);
}

void DMA2_Stream0_IRQHandler(void) { HAL_DMA_IRQHandler(&hdma); }

/* Повертає повний час "старт → готовність" у тактах (включаючи busy-wait) */
uint32_t bench_dma(void *d, void *s, size_t n) {
    dma_done = false;
    uint32_t t0 = cyc();
    /* у M2M джерело йде першим аргументом-адресою, а довжина рахується
       НЕ в байтах, а в елементах обраної розрядності — тут у словах */
    HAL_DMA_Start_IT(&hdma, (uint32_t)s, (uint32_t)d, n / 4);
    while (!dma_done) {}       /* busy-wait: ядро чекає завершення */
    uint32_t t1 = cyc();
    return t1 - t0;
}
