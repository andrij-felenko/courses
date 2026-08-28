// Круговий прийом у ПОДВІЙНИЙ буфер. Кожна половина — ціле число 32-байтних
// рядків, увесь буфер вирівняно на 32. Приймаємо суцільний потік без пауз.
#define HALF   64u              // одна половина = 64 байти = 2 рядки
#define FULL   (2u * HALF)      // 128 байтів = 4 рядки
static uint8_t stream_buf[FULL] __attribute__((aligned(32)));

static void stream_start(void)
{
    SCB_InvalidateDCache_by_Addr((uint32_t *)stream_buf, FULL);  // чисто під DMA
    dma_rx_config_circular((uint32_t)stream_buf, FULL);          // круговий режим
    dma_rx_enable_ht_tc();     // увімкнути ОБА переривання: HT і TC
}

void DMA1_Stream0_IRQHandler(void)
{
    if (dma_half_transfer_flag()) {        // готова НИЖНЯ половина
        dma_clear_ht_flag();
        // знедійснити й читати ЛИШЕ нижню; верхню DMA саме пише — не чіпати
        SCB_InvalidateDCache_by_Addr((uint32_t *)&stream_buf[0], HALF);
        process_half(&stream_buf[0], HALF);
    }
    if (dma_transfer_complete_flag()) {    // готова ВЕРХНЯ половина
        dma_clear_tc_flag();
        SCB_InvalidateDCache_by_Addr((uint32_t *)&stream_buf[HALF], HALF);
        process_half(&stream_buf[HALF], HALF);
    }
}
