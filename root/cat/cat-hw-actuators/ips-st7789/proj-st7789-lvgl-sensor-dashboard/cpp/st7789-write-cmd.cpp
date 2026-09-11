// Реалізація для Arduino Framework (C++)
#include <Arduino.h>
#include <SPI.h>
#include <lvgl.h>

#define ST7789_CMD_CASET 0x2A
#define ST7789_CMD_RASET 0x2B
#define ST7789_CMD_RAMWR 0x2C

#define ST7789_OFFSET_X  0
#define ST7789_OFFSET_Y  0

static const int PIN_DC = 2;
static const int PIN_CS = 5;

static inline void st7789_write_cmd(uint8_t cmd) {
    digitalWrite(PIN_DC, LOW);
    digitalWrite(PIN_CS, LOW);
    SPI.transfer(cmd);
    digitalWrite(PIN_CS, HIGH);
}

static inline void st7789_write_data(const uint8_t *data, size_t len) {
    digitalWrite(PIN_DC, HIGH);
    digitalWrite(PIN_CS, LOW);
    SPI.writeBytes(data, len);
    digitalWrite(PIN_CS, HIGH);
}

void disp_flush(lv_disp_drv_t *disp_drv, const lv_area_t *area, lv_color_t *color_p) {
    uint16_t x1 = area->x1 + ST7789_OFFSET_X;
    uint16_t x2 = area->x2 + ST7789_OFFSET_X;
    uint16_t y1 = area->y1 + ST7789_OFFSET_Y;
    uint16_t y2 = area->y2 + ST7789_OFFSET_Y;

    // Встановлення прямокутного вікна адресації
    st7789_write_cmd(ST7789_CMD_CASET);
    uint8_t cols[4] = {
        (uint8_t)(x1 >> 8), (uint8_t)(x1 & 0xFF),
        (uint8_t)(x2 >> 8), (uint8_t)(x2 & 0xFF)
    };
    st7789_write_data(cols, 4);

    st7789_write_cmd(ST7789_CMD_RASET);
    uint8_t rows[4] = {
        (uint8_t)(y1 >> 8), (uint8_t)(y1 & 0xFF),
        (uint8_t)(y2 >> 8), (uint8_t)(y2 & 0xFF)
    };
    st7789_write_data(rows, 4);

    // Запис масиву пікселів
    st7789_write_cmd(ST7789_CMD_RAMWR);
    uint32_t count = (area->x2 - area->x1 + 1) * (area->y2 - area->y1 + 1);
    st7789_write_data(reinterpret_cast<const uint8_t *>(color_p), count * sizeof(lv_color_t));

    // Сигнал готовності конвеєру LVGL
    lv_disp_flush_ready(disp_drv);
}

void displayDriverInit() {
    static lv_disp_draw_buf_t draw_buf;
    static lv_color_t buf[240 * 24]; // 1/10 висоти екрана 240x240

    lv_disp_draw_buf_init(&draw_buf, buf, nullptr, 240 * 24);

    static lv_disp_drv_t disp_drv;
    lv_disp_drv_init(&disp_drv);
    disp_drv.hor_res = 240;
    disp_drv.ver_res = 240;
    disp_drv.flush_cb = disp_flush;
    disp_drv.draw_buf = &draw_buf;

    lv_disp_drv_register(&disp_drv);
}
