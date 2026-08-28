// C implementation: Low-level OSD Line Injector using SPI DMA & EXTI HSYNC Interrupts
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define PAL_TOTAL_LINES    625
#define PAL_ACTIVE_PIXELS  320
#define OSD_LINE_BYTES     (PAL_ACTIVE_PIXELS / 8)
#define OSD_START_LINE     40
#define OSD_END_LINE       280

typedef struct {
    uint8_t line_buffer[OSD_LINE_BYTES];
    volatile uint16_t current_line;
    volatile bool is_active_frame;
    volatile bool dma_busy;
} osd_injector_t;

static osd_injector_t g_osd;

// Ініціалізація буферів та стану OSD
void osd_init(osd_injector_t *osd) {
    osd->current_line = 0;
    osd->is_active_frame = false;
    osd->dma_busy = false;
    memset((void*)osd->line_buffer, 0x00, OSD_LINE_BYTES);
}

// Очищення буфера рядка перед збіркою нового кадру
void osd_clear_buffer(osd_injector_t *osd) {
    memset((void*)osd->line_buffer, 0x00, OSD_LINE_BYTES);
}

// Запис точкового пікселя в маску рядка
void osd_draw_pixel(osd_injector_t *osd, uint16_t x) {
    if (x < PAL_ACTIVE_PIXELS) {
        uint16_t byte_idx = x / 8;
        uint8_t bit_idx = 7 - (x % 8);
        osd->line_buffer[byte_idx] |= (1 << bit_idx);
    }
}

// Обробник зовнішнього переривання HSYNC (рядкова синхронізація EXTI)
void EXTI_HSYNC_IRQHandler(osd_injector_t *osd) {
    osd->current_line++;
    
    // Перевірка, чи знаходиться промінь у робочій зоні кадру
    if (osd->current_line >= OSD_START_LINE && osd->current_line <= OSD_END_LINE) {
        // Апаратний запуск таймера затримки задньої площадки (10.5 мкс)
        // Після збігу таймер автономно ініціює DMA-передачу в SPI_DR
        osd->dma_busy = true;
    }
}

// Обробник зовнішнього переривання VSYNC (кадрова синхронізація EXTI)
void EXTI_VSYNC_IRQHandler(osd_injector_t *osd) {
    osd->current_line = 0; // Скидання лічильника рядків на початку кадру
    osd->is_active_frame = true;
}

// Зворотний виклик завершення DMA-передачі рядка
void DMA_SPI_TX_IRQHandler(osd_injector_t *osd) {
    osd->dma_busy = false;
}
