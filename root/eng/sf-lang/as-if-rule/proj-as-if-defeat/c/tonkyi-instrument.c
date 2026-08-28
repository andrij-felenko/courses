extern uint8_t dma_buf[64];
#define DMA_START  (*(volatile uint32_t *)0x40020000u)

void kick_dma(void)
{
    for (int i = 0; i < 64; i++)
        dma_buf[i] = compute(i);   /* 1) заповнюємо буфер (звичайна RAM) */

    DMA_START = 1u;                /* 2) команда старт (volatile-регістр) */
}
