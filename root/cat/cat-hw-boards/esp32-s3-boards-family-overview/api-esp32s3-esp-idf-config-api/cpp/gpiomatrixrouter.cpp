#include "driver/gpio.h"
#include "soc/gpio_sig_map.h"

class GpioMatrixRouter {
public:
    static esp_err_t routeUartTx(gpio_num_t pin) {
        gpio_config_t io_conf = {
            .pin_bit_mask = (1ULL << pin),
            .mode = GPIO_MODE_OUTPUT,
            .pull_up_en = GPIO_PULLUP_ENABLE,
            .pull_down_en = GPIO_PULLDOWN_DISABLE,
            .intr_type = GPIO_INTR_DISABLE,
        };
        esp_err_t err = gpio_config(&io_conf);
        if (err != ESP_OK) return err;

        gpio_matrix_out(pin, U1TXD_OUT_IDX, false, false);
        return ESP_OK;
    }
};
