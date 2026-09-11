#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define ST7789_CMD_RAMWR 0x2C

/* Тип покажчика на функцію зворотного виклику після завершення передачі DMA */
typedef void (*st7789_dma_cb_t)(void *user_data);

/* Апаратний шар (HAL) з підтримкою DMA */
typedef struct {
    void (*spi_write)(const uint8_t *data, size_t len);
    bool (*spi_dma_start)(const uint8_t *data, size_t len, st7789_dma_cb_t cb, void *user_data);
    bool (*spi_dma_is_busy)(void);
    void (*set_dc)(bool level);
    void (*set_cs)(bool level);
} st7789_hal_t;

/* Структура стану драйвера дисплея */
typedef struct {
    st7789_hal_t hal;
    st7789_dma_cb_t active_cb;
    void *active_user_data;
    volatile bool is_busy;
} st7789_t;

void st7789_set_address_window(st7789_t *dev, uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1);
uint16_t st7789_swap_bytes(uint16_t color);

/* Внутрішній обробник завершення передачі DMA */
static void st7789_dma_internal_callback(void *user_data)
{
    st7789_t *dev = (st7789_t *)user_data;
    if (!dev) {
        return;
    }

    dev->is_busy = false;

    /* Виклик зареєстрованого зворотного виклику користувача */
    if (dev->active_cb) {
        st7789_dma_cb_t cb = dev->active_cb;
        void *cb_data = dev->active_user_data;
        dev->active_cb = NULL;
        dev->active_user_data = NULL;
        cb(cb_data);
    }
}

/* Неблокувальний запуск передачі буфера пікселів через DMA */
bool st7789_write_stream_dma(st7789_t *dev, const void *data, size_t length,
                             st7789_dma_cb_t callback, void *user_data)
{
    if (!dev || !data || length == 0) {
        return false;
    }

    /* Перевірка доступності каналу DMA */
    if (dev->is_busy || dev->hal.spi_dma_is_busy()) {
        return false;
    }

    dev->active_cb = callback;
    dev->active_user_data = user_data;
    dev->is_busy = true;

    /* Налаштування ліній керування */
    dev->hal.set_cs(false);
    dev->hal.set_dc(true);

    /* Запуск апаратної передачі DMA */
    if (!dev->hal.spi_dma_start((const uint8_t *)data, length,
                                st7789_dma_internal_callback, dev)) {
        dev->is_busy = false;
        dev->hal.set_cs(true);
        return false;
    }

    return true;
}
