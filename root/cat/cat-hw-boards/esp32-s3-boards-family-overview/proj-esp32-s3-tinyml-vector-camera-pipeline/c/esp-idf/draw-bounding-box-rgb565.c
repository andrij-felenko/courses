#include "driver/spi_master.h"
#include "esp_lcd_panel_io.h"
#include "esp_lcd_panel_ops.h"
#include "esp_log.h"

static const char *TAG = "display_out";

// Малювання прямокутника оверлею (overlay) у буфері RGB565
void draw_bounding_box_rgb565(uint16_t *buffer, int img_w, int x, int y,
                              int w, int h, uint16_t color) {
    for (int i = x; i < x + w; ++i) {
        buffer[y * img_w + i] = color;
        buffer[(y + h) * img_w + i] = color;
    }
    for (int j = y; j < y + h; ++j) {
        buffer[j * img_w + x] = color;
        buffer[j * img_w + x + w] = color;
    }
}

void transmit_frame_dma(esp_lcd_panel_handle_t panel_handle,
                        uint16_t *frame_buffer, int x1, int y1, int x2, int y2) {
    // Асинхронне виведення кадру через DMA без блокування ЦП
    esp_lcd_panel_draw_bitmap(panel_handle, x1, y1, x2, y2, frame_buffer);
}
