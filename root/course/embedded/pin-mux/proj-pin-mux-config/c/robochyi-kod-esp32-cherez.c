#include "esp_rom_gpio.h"
#include "soc/gpio_sig_map.h"   // U1TXD_OUT_IDX, U1RXD_IN_IDX, …
#include "hal/gpio_hal.h"
#include "driver/gpio.h"

void uart1_pins_via_matrix(void) {
    const int tx_pin = 17;
    const int rx_pin = 16;

    // 1. Ніжку-вихід треба зробити виходом, ніжку-вхід — входом.
    //    Матриця тільки КОМУТУЄ; буфер ніжки (драйвер/приймач) вмикаємо окремо.
    gpio_set_direction(tx_pin, GPIO_MODE_OUTPUT);
    gpio_set_direction(rx_pin, GPIO_MODE_INPUT);

    // 2. ВИХІД: вести сигнал передавача U1TXD з блоку → на ніжку 17.
    //    (ніжка, індекс_сигналу, інвертувати_сигнал, інвертувати_дозвіл_виходу)
    esp_rom_gpio_connect_out_signal(tx_pin, U1TXD_OUT_IDX, false, false);

    // 3. ВХІД: завести сигнал з ніжки 16 → у приймач блоку U1RXD.
    //    (ніжка, індекс_сигналу, інвертувати_сигнал)
    esp_rom_gpio_connect_in_signal(rx_pin, U1RXD_IN_IDX, false);
}
