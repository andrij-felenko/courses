#include "stm32f4xx.h"   // CMSIS: дає CoreDebug, DWT, ITM

// Увімкнути лічильник тактів один раз на старті (Cortex-M3/M4/M7)
static void cyccnt_enable(void) {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;  // глобально ввімкнути DWT/ITM
    DWT->CYCCNT = 0;                                  // обнулити лічильник
    DWT->CTRL  |= DWT_CTRL_CYCCNTENA_Msk;            // пустити лік тактів
}

// Текстовий вивід одного символу через стимул-порт 0 ITM (як printf, але дешево)
static void itm_putc(char c) {
    if ((ITM->TCR & ITM_TCR_ITMENA_Msk) && (ITM->TER & 1u)) { // ITM і порт 0 ввімкнені
        while (ITM->PORT[0].u32 == 0) { }   // дочекатися місця у FIFO порту
        ITM->PORT[0].u8 = (uint8_t)c;       // запис байта = відправлення
    }
}

void DMA1_Stream0_IRQHandler(void) {
    uint32_t t0 = DWT->CYCCNT;   // знімок на вході — нічого не спиняємо

    handle_dma_transfer();       // власне тіло обробника

    uint32_t dt = DWT->CYCCNT - t0;   // різниця = тривалість у тактах
    // надсилаємо число на хост через ITM (тут — байт за байтом, спрощено)
    itm_putc('0' + (dt / 100) % 10);
    itm_putc('0' + (dt / 10)  % 10);
    itm_putc('0' +  dt        % 10);
    itm_putc('\n');
}
