#include <stdio.h>
#include "driver/gpio.h"
#include "esp_rom_gpio.h"
#include "soc/gpio_sig_map.h"
#include "esp_log.h"

static const char *TAG = "gpio_mux";

esp_err_t route_uart0_via_gpio_matrix(gpio_num_t tx_pin, gpio_num_t rx_pin)
{
    // Конфігурування напрямку роботи виводів GPIO для використання матрицею
    gpio_set_direction(tx_pin, GPIO_MODE_OUTPUT);
    gpio_set_direction(rx_pin, GPIO_MODE_INPUT);

    // Підключення фізичної ніжки tx_pin до виходу контролера U0TXD
    esp_rom_gpio_connect_out_signal(tx_pin, U0TXD_OUT_IDX, false, false);

    // Підключення входу контролера U0RXD до фізичної ніжки rx_pin
    esp_rom_gpio_connect_in_signal(rx_pin, U0RXD_IN_IDX, false);

    ESP_LOGI(TAG, "Сигнали UART0 успішно перенаправлені на GPIO%d (TX) та GPIO%d (RX)", tx_pin, rx_pin);
    return ESP_OK;
}
