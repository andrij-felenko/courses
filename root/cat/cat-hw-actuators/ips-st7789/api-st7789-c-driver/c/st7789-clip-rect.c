#include <stdint.h>
#include <stdbool.h>

#define ST7789_WIDTH   240
#define ST7789_HEIGHT  240

typedef enum {
    ST7789_OK          =  0,
    ST7789_ERR_PARAM   = -1,
    ST7789_ERR_TIMEOUT = -2
} st7789_status_t;

// Прямокутна область для малювання
typedef struct {
    int16_t x;
    int16_t y;
    int16_t w;
    int16_t h;
} st7789_rect_t;

// Параметри відсіченої області та зміщення вихідного буфера
typedef struct {
    uint16_t x_start;
    uint16_t y_start;
    uint16_t x_end;
    uint16_t y_end;
    uint16_t src_x_offset;
    uint16_t src_y_offset;
    uint16_t visible_w;
    uint16_t visible_h;
} st7789_clipped_rect_t;

// Апаратно-залежні виклики
typedef struct {
    void (*set_cs)(uint8_t level);
    void (*set_dc)(uint8_t level);
    void (*set_res)(uint8_t level);
    void (*spi_write_byte)(uint8_t data);
    void (*spi_write_dma)(const uint8_t *data, uint32_t len);
    void (*dma_abort)(void);
    uint32_t (*get_tick_ms)(void);
    void (*delay_ms)(uint32_t ms);
    void (*delay_us)(uint32_t us);
} st7789_hal_t;

typedef struct {
    st7789_hal_t hal;
    volatile bool dma_busy;
    uint8_t madctl_backup;
} st7789_driver_t;

// Розрахунок відсікання прямокутника межами видимого екрана 240x240
bool st7789_clip_rect(const st7789_rect_t *in_rect, st7789_clipped_rect_t *out_clip) {
    if (!in_rect || !out_clip || in_rect->w <= 0 || in_rect->h <= 0) {
        return false;
    }

    // Перевірка повного виходу за межі екрана
    if (in_rect->x >= ST7789_WIDTH || in_rect->y >= ST7789_HEIGHT ||
        (in_rect->x + in_rect->w) <= 0 || (in_rect->y + in_rect->h) <= 0) {
        return false;
    }

    // Обчислення горизонтального перетину
    int16_t x0 = in_rect->x;
    int16_t x1 = in_rect->x + in_rect->w - 1;
    out_clip->src_x_offset = (x0 < 0) ? (uint16_t)(-x0) : 0;
    out_clip->x_start = (x0 < 0) ? 0 : (uint16_t)x0;
    out_clip->x_end   = (x1 >= ST7789_WIDTH) ? (ST7789_WIDTH - 1) : (uint16_t)x1;
    out_clip->visible_w = out_clip->x_end - out_clip->x_start + 1;

    // Обчислення вертикального перетину
    int16_t y0 = in_rect->y;
    int16_t y1 = in_rect->y + in_rect->h - 1;
    out_clip->src_y_offset = (y0 < 0) ? (uint16_t)(-y0) : 0;
    out_clip->y_start = (y0 < 0) ? 0 : (uint16_t)y0;
    out_clip->y_end   = (y1 >= ST7789_HEIGHT) ? (ST7789_HEIGHT - 1) : (uint16_t)y1;
    out_clip->visible_h = out_clip->y_end - out_clip->y_start + 1;

    return true;
}

// Запис однієї команди зі стробуванням CS
static void st7789_write_cmd(st7789_driver_t *drv, uint8_t cmd) {
    drv->hal.set_dc(0);
    drv->hal.set_cs(0);
    drv->hal.spi_write_byte(cmd);
    drv->hal.set_cs(1); // Стробування: підняття CS після команди скидає лічильник бітів
}

// Запис команди з параметрами
static void st7789_write_cmd_data(st7789_driver_t *drv, uint8_t cmd, const uint8_t *data, uint32_t len) {
    drv->hal.set_dc(0);
    drv->hal.set_cs(0);
    drv->hal.spi_write_byte(cmd);
    if (data && len > 0) {
        drv->hal.set_dc(1);
        for (uint32_t i = 0; i < len; ++i) {
            drv->hal.spi_write_byte(data[i]);
        }
    }
    drv->hal.set_cs(1); // Стробування CS після завершення пакету
}

// Очікування завершення передачі DMA із захистом від зависання
st7789_status_t st7789_wait_dma_finish(st7789_driver_t *drv, uint32_t timeout_ms) {
    uint32_t start_tick = drv->hal.get_tick_ms();
    while (drv->dma_busy) {
        if ((drv->hal.get_tick_ms() - start_tick) > timeout_ms) {
            drv->hal.dma_abort();
            drv->hal.set_cs(1); // Апаратне підняття CS відновлює бітову синхронізацію
            drv->dma_busy = false;
            return ST7789_ERR_TIMEOUT;
        }
    }
    return ST7789_OK;
}

// Алгоритм швидкого відновлення дисплея без знеструмлення
st7789_status_t st7789_recover(st7789_driver_t *drv) {
    if (!drv) {
        return ST7789_ERR_PARAM;
    }

    // 1. Аварійна зупинка шини та переведення CS у пасивний стан
    drv->hal.dma_abort();
    drv->hal.set_cs(1);
    drv->dma_busy = false;

    // 2. Апаратне або програмне скидання контролера
    if (drv->hal.set_res) {
        drv->hal.set_res(0);
        drv->hal.delay_us(20); // Імпульс скидання мінімум 10 мкс
        drv->hal.set_res(1);
        drv->hal.delay_ms(120); // Очікування завантаження калібрувань із OTP
    } else {
        st7789_write_cmd(drv, 0x01); // Команда SWRESET
        drv->hal.delay_ms(120);
    }

    // 3. Вихід зі сплячого режиму
    st7789_write_cmd(drv, 0x11); // Команда SLPOUT
    drv->hal.delay_ms(120);       // Очікування стабілізації помпи заряду

    // 4. Відновлення обов'язкових конфігураційних регістрів
    uint8_t colmod_val = 0x55;   // 16 бітів на піксель (RGB565)
    st7789_write_cmd_data(drv, 0x3A, &colmod_val, 1);

    uint8_t madctl_val = drv->madctl_backup;
    st7789_write_cmd_data(drv, 0x36, &madctl_val, 1);

    st7789_write_cmd(drv, 0x21); // INVON: обов'язкова інверсія для IPS
    st7789_write_cmd(drv, 0x13); // NORON: звичайний режим роботи
    st7789_write_cmd(drv, 0x29); // DISPON: увімкнення екрана
    drv->hal.delay_ms(10);

    // 5. Очищення відеопам'яті чорним кольором (стирання шуму)
    uint8_t caset_data[4] = {0x00, 0x00, 0x00, (ST7789_WIDTH - 1)};
    uint8_t raset_data[4] = {0x00, 0x00, 0x00, (ST7789_HEIGHT - 1)};
    st7789_write_cmd_data(drv, 0x2A, caset_data, 4);
    st7789_write_cmd_data(drv, 0x2B, raset_data, 4);

    drv->hal.set_dc(0);
    drv->hal.set_cs(0);
    drv->hal.spi_write_byte(0x2C); // RAMWR
    drv->hal.set_dc(1);

    for (uint32_t i = 0; i < (ST7789_WIDTH * ST7789_HEIGHT * 2); ++i) {
        drv->hal.spi_write_byte(0x00);
    }
    drv->hal.set_cs(1); // Стробування CS після очищення екрана

    return ST7789_OK;
}
