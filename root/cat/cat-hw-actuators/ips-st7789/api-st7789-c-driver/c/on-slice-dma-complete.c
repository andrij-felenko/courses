#define DISPLAY_WIDTH   240
#define DISPLAY_HEIGHT  240
#define SLICE_LINES     16
#define SLICE_PIXELS    (DISPLAY_WIDTH * SLICE_LINES)
#define TOTAL_SLICES    (DISPLAY_HEIGHT / SLICE_LINES)

/* Контекст подвійної буферизації */
typedef struct {
    uint16_t buffer_a[SLICE_PIXELS];
    uint16_t buffer_b[SLICE_PIXELS];
    volatile bool dma_done;
} pipeline_context_t;

/* Зворотний виклик після завершення відправки смуги */
static void on_slice_dma_complete(void *user_data)
{
    pipeline_context_t *ctx = (pipeline_context_t *)user_data;
    ctx->dma_done = true;
}

/* Виведення кадру через чергування буферів */
void render_frame_ping_pong(st7789_t *dev)
{
    static pipeline_context_t ctx;
    ctx.dma_done = true;

    /* Встановлення вікна адресації на всю площу дисплея */
    st7789_set_address_window(dev, 0, 0, DISPLAY_WIDTH - 1, DISPLAY_HEIGHT - 1);

    /* Надсилання команди початку запису в пам'ять */
    uint8_t cmd = ST7789_CMD_RAMWR;
    dev->hal.set_cs(false);
    dev->hal.set_dc(false);
    dev->hal.spi_write(&cmd, 1);

    uint16_t *render_buf = ctx.buffer_a;
    uint16_t *transmit_buf = ctx.buffer_b;

    for (size_t slice = 0; slice < TOTAL_SLICES; ++slice) {
        /* 1. Рендеринг поточної смуги процесором у буфер render_buf */
        uint16_t start_y = (uint16_t)(slice * SLICE_LINES);
        for (size_t i = 0; i < SLICE_PIXELS; ++i) {
            render_buf[i] = st7789_swap_bytes((uint16_t)(start_y + (i % DISPLAY_WIDTH)));
        }

        /* 2. Очікування завершення попередньої передачі DMA */
        while (!ctx.dma_done) {
        }
        ctx.dma_done = false;

        /* 3. Перемикання вказівників буферів */
        uint16_t *temp = render_buf;
        render_buf = transmit_buf;
        transmit_buf = temp;

        /* 4. Запуск DMA-передачі підготовленої смуги */
        st7789_write_stream_dma(dev, transmit_buf, SLICE_PIXELS * sizeof(uint16_t),
                                on_slice_dma_complete, &ctx);
    }

    /* Очікування виведення останньої смуги кадру */
    while (!ctx.dma_done) {
    }

    /* Завершення передачі кадру */
    dev->hal.set_cs(true);
}
