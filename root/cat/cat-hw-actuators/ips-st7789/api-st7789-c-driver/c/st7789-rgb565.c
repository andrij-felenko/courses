#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* Команда контролера ST7789 для запису в пам'ять кадру */
#define ST7789_CMD_RAMWR 0x2C

/* Розмір проміжного буфера пакета для швидкого заливання */
#define ST7789_FILL_BUF_PIXELS 64

/* Інтерфейс апаратного рівня (HAL) */
typedef struct {
    void (*spi_write)(const uint8_t *data, size_t len);
    void (*set_dc)(bool level);
    void (*set_cs)(bool level);
} st7789_hal_t;

/* Описова структура дисплея */
typedef struct {
    st7789_hal_t hal;
    uint16_t width;
    uint16_t height;
} st7789_t;

/* Оголошення функції встановлення вікна адресації */
void st7789_set_address_window(st7789_t *dev, uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1);

/* Пакування 8-бітних компонентів у 16-бітне значення RGB565 */
static inline uint16_t st7789_rgb565(uint8_t r, uint8_t g, uint8_t b)
{
    return (uint16_t)(((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3));
}

/* Перестановка байтів із Little-Endian у Big-Endian */
static inline uint16_t st7789_swap_bytes(uint16_t color)
{
#if defined(__GNUC__) || defined(__clang__)
    return __builtin_bswap16(color);
#else
    return (uint16_t)((color >> 8) | (color << 8));
#endif
}

/* Виведення довільного масиву пікселів у відкрите вікно адресації */
void st7789_write_pixels(st7789_t *dev, const uint16_t *pixels, size_t count)
{
    if (!dev || !pixels || count == 0) {
        return;
    }

    uint8_t cmd = ST7789_CMD_RAMWR;

    /* Активація вибору чипа та передача команди запису в пам'ять */
    dev->hal.set_cs(false);
    dev->hal.set_dc(false);
    dev->hal.spi_write(&cmd, 1);

    /* Перемикання лінії D/C у стан даних */
    dev->hal.set_dc(true);

    /* Відправка масиву пікселів як послідовності байтів */
    dev->hal.spi_write((const uint8_t *)pixels, count * sizeof(uint16_t));

    /* Деактивація чипа */
    dev->hal.set_cs(true);
}

/* Швидке суцільне заливання прямокутної області одним кольором */
void st7789_fill_color(st7789_t *dev, uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint16_t color)
{
    if (!dev || w == 0 || h == 0) {
        return;
    }

    /* Встановлення меж прямокутного вікна */
    st7789_set_address_window(dev, x, y, (uint16_t)(x + w - 1), (uint16_t)(y + h - 1));

    uint8_t cmd = ST7789_CMD_RAMWR;
    dev->hal.set_cs(false);
    dev->hal.set_dc(false);
    dev->hal.spi_write(&cmd, 1);
    dev->hal.set_dc(true);

    /* Підготовка значення кольору у форматі Big-Endian */
    uint16_t be_color = st7789_swap_bytes(color);

    /* Формування локального пакета пікселів для групової передачі */
    uint16_t batch_buffer[ST7789_FILL_BUF_PIXELS];
    for (size_t i = 0; i < ST7789_FILL_BUF_PIXELS; ++i) {
        batch_buffer[i] = be_color;
    }

    size_t total_pixels = (size_t)w * (size_t)h;
    size_t full_batches = total_pixels / ST7789_FILL_BUF_PIXELS;
    size_t rem_pixels   = total_pixels % ST7789_FILL_BUF_PIXELS;

    /* Передача повних пакетів */
    for (size_t i = 0; i < full_batches; ++i) {
        dev->hal.spi_write((const uint8_t *)batch_buffer, sizeof(batch_buffer));
    }

    /* Передача залишку пікселів */
    if (rem_pixels > 0) {
        dev->hal.spi_write((const uint8_t *)batch_buffer, rem_pixels * sizeof(uint16_t));
    }

    dev->hal.set_cs(true);
}
