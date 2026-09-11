#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define ST7789_WIDTH        240
#define ST7789_HEIGHT       240
#define ST7789_BLOCK_LINES  16
#define ST7789_BLOCK_PIXELS (ST7789_WIDTH * ST7789_BLOCK_LINES)
#define ST7789_BLOCK_BYTES  (ST7789_BLOCK_PIXELS * 2)

// Два виділені буфери для асинхронного конвеєра пінг-понг
static uint8_t line_buffer_a[ST7789_BLOCK_BYTES];
static uint8_t line_buffer_b[ST7789_BLOCK_BYTES];

// Прапорець стану активності апаратної передачі DMA
static volatile bool dma_transfer_active = false;

// Функція зворотного виклику, що спрацьовує в перериванні DMA
void st7789_dma_transfer_complete_isr(void)
{
    dma_transfer_active = false;
}

// Прототипи апаратних функцій платформи
extern void platform_spi_dma_start(const uint8_t *data, size_t length);
extern void platform_spi_dma_wait(void);
extern void st7789_set_address_window(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1);
extern void render_scene_slice(uint16_t start_line, uint16_t line_count, uint16_t *output_buffer);

// Виведення повного кадру через подвійний буфер і DMA
void st7789_render_frame_dma(void)
{
    uint8_t *render_buf = line_buffer_a;
    uint8_t *dma_buf = line_buffer_b;

    for (uint16_t y = 0; y < ST7789_HEIGHT; y += ST7789_BLOCK_LINES) {
        // Крок 1: Ядро процесора заповнює активний буфер пікселями
        render_scene_slice(y, ST7789_BLOCK_LINES, (uint16_t *)render_buf);

        // Крок 2: Очікуємо завершення передачі попереднього блоку
        while (dma_transfer_active) {
            // Очікування переривання від DMA (наприклад, інструкція WFI)
        }

        // Крок 3: Встановлюємо прямокутне вікно контролера ST7789
        st7789_set_address_window(0, y, ST7789_WIDTH - 1, y + ST7789_BLOCK_LINES - 1);

        // Крок 4: Запускаємо апаратний DMA для щойно заповненого буфера
        dma_transfer_active = true;
        platform_spi_dma_start(render_buf, ST7789_BLOCK_BYTES);

        // Крок 5: Міняємо буфери місцями для наступної ітерації конвеєра
        uint8_t *temp = render_buf;
        render_buf = dma_buf;
        dma_buf = temp;
    }

    // Дочекатися завершення передачі останньої смуги перед виходом
    while (dma_transfer_active) {
    }
}
