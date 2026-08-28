#include "driver/spi_master.h"

// ── Варіант А: ніжки VSPI з IO_MUX → драйвер бере прямий шлях, повна швидкість ──
static void spi_fast_iomux(void) {
    spi_bus_config_t bus = {
        .sclk_io_num = 18,   // ← рекомендовані IO_MUX-виводи VSPI
        .mosi_io_num = 23,
        .miso_io_num = 19,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
    };
    spi_bus_initialize(SPI3_HOST, &bus, SPI_DMA_CH_AUTO);

    spi_device_interface_config_t dev = {
        .clock_speed_hz = 80 * 1000 * 1000,  // 80 МГц — реально лише через IO_MUX
        .spics_io_num   = 5,                  // ← CS теж IO_MUX-виводу VSPI
        .mode = 0, .queue_size = 4,
    };
    spi_device_handle_t h;
    spi_bus_add_device(SPI3_HOST, &dev, &h);
    // Тут драйвер побачив: усі ніжки = IO_MUX VSPI → матриця вимкнена, прямий шлях.
}

// ── Варіант Б: довільні ніжки → драйвер вмикає матрицю, стеля падає ──
static void spi_slow_matrix(void) {
    spi_bus_config_t bus = {
        .sclk_io_num = 25,   // ← НЕ IO_MUX-виводи: вибрані під зручність плати
        .mosi_io_num = 26,
        .miso_io_num = 27,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
    };
    spi_bus_initialize(SPI3_HOST, &bus, SPI_DMA_CH_AUTO);

    spi_device_interface_config_t dev = {
        .clock_speed_hz = 80 * 1000 * 1000,  // ПОПРОСИЛИ 80 — але через матрицю
        .spics_io_num   = 33,                 //   стеля ~26–40 МГц: на 80 шина збоїть
        .mode = 0, .queue_size = 4,
    };
    spi_device_handle_t h;
    spi_bus_add_device(SPI3_HOST, &dev, &h);
    // Драйвер побачив чужі ніжки → увімкнув матрицю для ВСІХ сигналів шини.
}
