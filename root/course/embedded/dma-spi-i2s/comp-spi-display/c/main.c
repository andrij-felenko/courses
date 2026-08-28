#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "esp_heap_caps.h"

#define LCD_W   240
#define LCD_H   320
#define CHUNK_H  16          /* рядків в одному DMA-блоці */
#define PIN_DC   GPIO_NUM_2
#define PIN_RST  GPIO_NUM_4

spi_device_handle_t dev;

/* Буфери DMA-придатні (пам'ять для DMA особлива — MALLOC_CAP_DMA) */
static uint16_t *fb[2];

/* Допоміжна функція: послати команду (DC=0) або дані (DC=1) */
static void lcd_cmd(uint8_t cmd, const uint8_t *data, int len)
{
    spi_transaction_t t = { .length = 8, .tx_buffer = &cmd };
    gpio_set_level(PIN_DC, 0);           /* DC=0 → байт-команда */
    spi_device_polling_transmit(dev, &t);
    if (data && len > 0) {
        spi_transaction_t td = { .length = len * 8, .tx_buffer = data };
        gpio_set_level(PIN_DC, 1);       /* DC=1 → дані команди */
        spi_device_polling_transmit(dev, &td);
    }
}

/* Встановити вікно адрес (колонки і рядки) */
static void lcd_set_window(uint16_t x0, uint16_t y0,
                           uint16_t x1, uint16_t y1)
{
    uint8_t p[4];
    p[0]=x0>>8; p[1]=x0&0xFF; p[2]=x1>>8; p[3]=x1&0xFF;
    lcd_cmd(0x2A, p, 4);                 /* Column Address Set */
    p[0]=y0>>8; p[1]=y0&0xFF; p[2]=y1>>8; p[3]=y1&0xFF;
    lcd_cmd(0x2B, p, 4);                 /* Row Address Set */
    lcd_cmd(0x2C, NULL, 0);             /* Memory Write — далі пікселі */
    gpio_set_level(PIN_DC, 1);           /* DC=1 → пікселі */
}

/* Надіслати один DMA-chunk (неблокуючи) */
static spi_transaction_t trx;
static void lcd_send_chunk(uint16_t *buf, int pixels)
{
    trx = (spi_transaction_t){
        .length    = pixels * 16,        /* біти */
        .tx_buffer = buf,
    };
    spi_device_queue_trans(dev, &trx, portMAX_DELAY);
}

/* Чекати завершення попередньої DMA-транзакції */
static void lcd_wait()
{
    spi_transaction_t *res;
    spi_device_get_trans_result(dev, &res, portMAX_DELAY);
}

/* --- Ініціалізація шини --- */
void lcd_init_bus(void)
{
    spi_bus_config_t bus = {
        .mosi_io_num = GPIO_NUM_13,
        .sclk_io_num = GPIO_NUM_14,
        .miso_io_num = -1,
        .max_transfer_sz = LCD_W * CHUNK_H * 2, /* байтів на chunk */
    };
    spi_bus_initialize(SPI2_HOST, &bus, SPI_DMA_CH_AUTO);

    spi_device_interface_config_t dcfg = {
        .clock_speed_hz = 40 * 1000 * 1000,
        .mode           = 0,
        .spics_io_num   = GPIO_NUM_15,
        .queue_size     = 1,
    };
    spi_bus_add_device(SPI2_HOST, &dcfg, &dev);

    /* DMA-придатні буфери (звичайний malloc тут не годиться) */
    fb[0] = heap_caps_malloc(LCD_W * CHUNK_H * 2, MALLOC_CAP_DMA);
    fb[1] = heap_caps_malloc(LCD_W * CHUNK_H * 2, MALLOC_CAP_DMA);

    /* Після RST шлють ініт-послідовність контролера (≥120 команд ILI9341) */
    /* ... gpio RST low/high, sleep-out, display-on, color-mode RGB565 ... */
}

/* --- Головний цикл ping-pong: оновити весь кадр chunk-ами --- */
void lcd_flush_frame(void (*render_chunk)(uint16_t *buf, int y, int h))
{
    int cur = 0;
    lcd_set_window(0, 0, LCD_W - 1, LCD_H - 1);

    /* Заповнити перший буфер, поки DMA ще не стартував */
    render_chunk(fb[cur], 0, CHUNK_H);

    for (int y = 0; y < LCD_H; y += CHUNK_H) {
        lcd_send_chunk(fb[cur], LCD_W * CHUNK_H);   /* DMA жене fb[cur] */
        int next = cur ^ 1;
        int ny   = y + CHUNK_H;
        if (ny < LCD_H)
            render_chunk(fb[next], ny, CHUNK_H);    /* ядро малює fb[next] */
        lcd_wait();                                 /* чекати ЦЕЙ chunk */
        cur = next;
    }
}
