#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

/* Тестування всіх 4 режимів через закорочені виводи MOSI та MISO */
bool spi_bb_run_loopback_test(const spi_bitbang_t *bus_template) {
    const uint8_t test_patterns[] = {0x00, 0xFF, 0xAA, 0x55, 0xA5, 0x5A, 0xC3, 0x3C};
    const size_t num_patterns = sizeof(test_patterns) / sizeof(test_patterns[0]);

    spi_bitbang_t test_bus = *bus_template;

    for (int mode = 0; mode < 4; ++mode) {
        test_bus.mode = (spi_bb_mode_t)mode;
        spi_bb_init(&test_bus);

        for (size_t i = 0; i < num_patterns; ++i) {
            uint8_t tx = test_patterns[i];
            test_bus.set_cs(false);
            test_bus.delay_ns(test_bus.half_period_ns);

            uint8_t rx = spi_bb_transfer_byte(&test_bus, tx);

            test_bus.delay_ns(test_bus.half_period_ns);
            test_bus.set_cs(true);

            if (rx != tx) {
                /* Помилка: невідповідність отриманого байта переданому */
                return false;
            }
        }
    }
    return true;
}
