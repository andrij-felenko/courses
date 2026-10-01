#include "driver/gpio.h"
#include "soc/uart_reg.h"
#include "soc/gpio_sig_map.h"

void configure_uart_gpio_matrix(void) {
    // 1. Конфігурація фізичного виводу GPIO17 на вихід
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << GPIO_NUM_17),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&io_conf);

    // 2. Маршрутизація сигналу U1TXD_OUT через GPIO Matrix на GPIO17
    gpio_matrix_out(GPIO_NUM_17, U1TXD_OUT_IDX, false, false);
}
