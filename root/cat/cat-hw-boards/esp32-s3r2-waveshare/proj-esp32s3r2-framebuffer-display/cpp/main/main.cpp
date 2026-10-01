#include <cstdio>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "psram_frame_buffer.hpp"

static const char* TAG = "MAIN";

// Конфігурація роздільної здатності кадру
constexpr uint16_t FRAME_WIDTH = 320;
constexpr uint16_t FRAME_HEIGHT = 240;

// Умовні піни SPI для демонстрації DMA шини
constexpr gpio_num_t PIN_NUM_MOSI = GPIO_NUM_11;
constexpr gpio_num_t PIN_NUM_CLK  = GPIO_NUM_12;
constexpr gpio_num_t PIN_NUM_CS   = GPIO_NUM_10;

// Функція генерації кольорового градієнта (RGB565)
static void render_color_pattern(uint16_t* buffer, uint16_t width, uint16_t height, uint8_t frame_index) {
    for (uint16_t y = 0; y < height; ++y) {
        for (uint16_t x = 0; x < width; ++x) {
            uint8_t r = (x + frame_index) & 0x1F;
            uint8_t g = (y + frame_index) & 0x3F;
            uint8_t b = (x + y + frame_index) & 0x1F;
            buffer[y * width + x] = (r << 11) | (g << 5) | b;
        }
    }
}

extern "C" void app_main(void) {
    ESP_LOGI(TAG, "Запуск демонстрації подвійного кадрового буфера PSRAM на Waveshare ESP32-S3R2");

    // 1. Ініціалізація шини SPI з підтримкою DMA
    spi_bus_config_t buscfg = {};
    buscfg.mosi_io_num = PIN_NUM_MOSI;
    buscfg.miso_io_num = -1;
    buscfg.sclk_io_num = PIN_NUM_CLK;
    buscfg.quadwp_io_num = -1;
    buscfg.quadhd_io_num = -1;
    buscfg.max_transfer_sz = FRAME_WIDTH * FRAME_HEIGHT * sizeof(uint16_t);

    esp_err_t ret = spi_bus_initialize(SPI2_HOST, &buscfg, SPI_DMA_CH_AUTO);
    ESP_ERROR_CHECK(ret);

    spi_device_interface_config_t devcfg = {};
    devcfg.clock_speed_hz = 40 * 1000 * 1000; // 40 МГц
    devcfg.mode = 0;
    devcfg.spics_io_num = PIN_NUM_CS;
    devcfg.queue_size = 2; // Підтримка черги на 2 транзакції для ping-pong

    spi_device_handle_t spi_handle;
    ret = spi_bus_add_device(SPI2_HOST, &devcfg, &spi_handle);
    ESP_ERROR_CHECK(ret);

    try {
        // 2. Створення об'єкта кадрового буфера в PSRAM через RAII
        graphics::PsramFrameBuffer frame_buffer(FRAME_WIDTH, FRAME_HEIGHT);

        uint8_t frame_counter = 0;
        ESP_LOGI(TAG, "Початок циклу рендерингу та фонової DMA відправки...");

        while (true) {
            // Отримуємо вказівник на активний буфер малювання
            uint16_t* draw_buf = frame_buffer.get_draw_buffer();

            // Малюємо тестовий кадр у задньому буфері
            render_color_pattern(draw_buf, FRAME_WIDTH, FRAME_HEIGHT, frame_counter++);

            // Перемикаємо буфери (Ping-Pong): готовий кадр стає фронтальним
            frame_buffer.swap_buffers();

            // Відправляємо новий фронтальний буфер у дисплей асинхронно через DMA
            ret = frame_buffer.flush_async(spi_handle);
            if (ret != ESP_OK) {
                ESP_LOGE(TAG, "Помилка виклику flush_async");
            }

            vTaskDelay(pdMS_TO_TICKS(16)); // ~60 FPS
        }

    } catch (const std::exception& e) {
        ESP_LOGE(TAG, "Спіймано виняток: %s", e.what());
    }

    // Очищення ресурсів SPI при виході
    spi_bus_remove_device(spi_handle);
    spi_bus_free(SPI2_HOST);
}
