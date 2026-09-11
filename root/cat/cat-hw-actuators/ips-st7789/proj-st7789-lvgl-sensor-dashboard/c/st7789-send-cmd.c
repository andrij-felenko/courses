// Реалізація для ESP-IDF (чистий C)
#include "esp_log.h"
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "lvgl.h"

#define ST7789_CMD_CASET  0x2A
#define ST7789_CMD_RASET  0x2B
#define ST7789_CMD_RAMWR  0x2C

#define ST7789_OFFSET_X   0
#define ST7789_OFFSET_Y   0

static spi_device_handle_t spi_disp_handle;
static gpio_num_t pin_dc;

// Відправлення однобайтової команди на лінію SPI
static void st7789_send_cmd(uint8_t cmd) {
    gpio_set_level(pin_dc, 0); // Рівень 0 на лінії DC означає команду
    spi_transaction_t t = {
        .length = 8,
        .tx_buffer = &cmd,
    };
    spi_device_polling_transmit(spi_disp_handle, &t);
}

// Відправлення блоку даних пікселів або параметрів
static void st7789_send_data(const uint8_t *data, size_t len) {
    if (len == 0) return;
    gpio_set_level(pin_dc, 1); // Рівень 1 на лінії DC означає дані
    spi_transaction_t t = {
        .length = len * 8,
        .tx_buffer = data,
    };
    spi_device_polling_transmit(spi_disp_handle, &t);
}

// Зворотний виклик LVGL для передачі відрендереної ділянки
void disp_flush(lv_disp_drv_t *disp_drv, const lv_area_t *area, lv_color_t *color_p) {
    uint16_t x1 = area->x1 + ST7789_OFFSET_X;
    uint16_t x2 = area->x2 + ST7789_OFFSET_X;
    uint16_t y1 = area->y1 + ST7789_OFFSET_Y;
    uint16_t y2 = area->y2 + ST7789_OFFSET_Y;

    // Встановлення діапазону колонок
    st7789_send_cmd(ST7789_CMD_CASET);
    uint8_t col_data[4] = {
        (uint8_t)(x1 >> 8), (uint8_t)(x1 & 0xFF),
        (uint8_t)(x2 >> 8), (uint8_t)(x2 & 0xFF)
    };
    st7789_send_data(col_data, sizeof(col_data));

    // Встановлення діапазону рядків
    st7789_send_cmd(ST7789_CMD_RASET);
    uint8_t row_data[4] = {
        (uint8_t)(y1 >> 8), (uint8_t)(y1 & 0xFF),
        (uint8_t)(y2 >> 8), (uint8_t)(y2 & 0xFF)
    };
    st7789_send_data(row_data, sizeof(row_data));

    // Команда запису у відеопам'ять
    st7789_send_cmd(ST7789_CMD_RAMWR);

    // Розрахунок кількості байтів у масиві пікселів
    uint32_t width = (x2 - x1 + 1);
    uint32_t height = (y2 - y1 + 1);
    uint32_t byte_count = width * height * sizeof(lv_color_t);

    // Синхронна передача масиву кольорів по шині SPI
    st7789_send_data((const uint8_t *)color_p, byte_count);

    // Обов'язкове розблокування конвеєра після завершення передачі
    lv_disp_flush_ready(disp_drv);
}

// Ініціалізація та реєстрація драйвера в LVGL
void display_driver_init(void) {
    static lv_disp_draw_buf_t draw_buf;
    static lv_color_t buf[240 * 24]; // Буфер на 1/10 площі екрана

    lv_disp_draw_buf_init(&draw_buf, buf, NULL, 240 * 24);

    static lv_disp_drv_t disp_drv;
    lv_disp_drv_init(&disp_drv);
    disp_drv.hor_res = 240;
    disp_drv.ver_res = 240;
    disp_drv.flush_cb = disp_flush;
    disp_drv.draw_buf = &draw_buf;

    lv_disp_drv_register(&disp_drv);
}
