// C (ESP-IDF / STM32 HAL DMA & Interrupt approach)
#include <stdint.h>
#include <stdbool.h>

extern void spi_dma_transfer_start(const uint8_t *buffer, size_t size);
extern void st7789_set_ramwr(void);

static volatile bool ready_to_render = false;
static const uint8_t *current_frame_buffer = NULL;
static size_t frame_size_bytes = 0;

// Обробок апаратного переривання від лінії TE (V-Sync)
void IRAM_ATTR st7789_te_gpio_isr_handler(void* arg) {
    if (ready_to_render && current_frame_buffer != NULL) {
        st7789_set_ramwr();
        spi_dma_transfer_start(current_frame_buffer, frame_size_bytes);
        ready_to_render = false; // Блокування до закінчення рендерингу наступного кадру
    }
}

void st7789_trigger_frame_async(const uint8_t *frame_ptr, size_t size) {
    current_frame_buffer = frame_ptr;
    frame_size_bytes = size;
    ready_to_render = true; // Дозвіл запуску DMA на наступній павзі V-Blanking
}
