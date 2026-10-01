#include "driver/gpio.h"
#include "esp_rom_gpio.h"
#include "soc/gpio_sig_map.h"
#include "esp_log.h"

class GpioMatrixRouter {
public:
    static esp_err_t RouteUart0(gpio_num_t tx_pin, gpio_num_t rx_pin) {
        gpio_set_direction(tx_pin, GPIO_MODE_OUTPUT);
        gpio_set_direction(rx_pin, GPIO_MODE_INPUT);

        // Комутація вихідного та вхідного сигналів через GPIO Matrix
        esp_rom_gpio_connect_out_signal(tx_pin, U0TXD_OUT_IDX, false, false);
        esp_rom_gpio_connect_in_signal(rx_pin, U0RXD_IN_IDX, false);

        ESP_LOGI("GpioMatrixRouter", "Перенаправлено UART0 на GPIO%d/GPIO%d", tx_pin, rx_pin);
        return ESP_OK;
    }
};
