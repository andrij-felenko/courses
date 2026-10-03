#include "driver/spi_master.h"
#include "esp_lcd_panel_io.h"
#include "esp_lcd_panel_ops.h"
#include "esp_log.h"

class DisplayPipeline {
public:
    explicit DisplayPipeline(esp_lcd_panel_handle_t handle) : panel_handle_(handle) {}

    void draw_overlay_and_swap(uint16_t* active_buf, int width, int x, int y,
                              int w, int h, uint16_t color) {
        // Оверлейне малювання прямокутника результату розпізнавання
        for (int i = x; i < x + w; ++i) {
            active_buf[y * width + i] = color;
            active_buf[(y + h) * width + i] = color;
        }
        // Асинхронна передача кадру через апаратне DMA
        esp_lcd_panel_draw_bitmap(panel_handle_, 0, 0, width, height, active_buf);
    }

private:
    esp_lcd_panel_handle_t panel_handle_;
};
