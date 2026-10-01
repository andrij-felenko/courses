#include "driver/gpio.h"
#include "hal/gpio_types.h"

void configure_gpio_matrix_demo(void)
{
    // Конфігурація виводу GPIO4 як виходу за допомогою драйвера ESP-IDF
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << GPIO_NUM_4),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);

    // Маршрутизація внутрішнього сигналу UART1 TXD на фізичний вивід GPIO4 через GPIO Matrix
    // Сигнал отримує детерміновану затримку 1-2 такти шини APB (12.5-25 нс)
    gpio_matrix_out(GPIO_NUM_4, UART_NUM_1_TXD_IDX, false, false);
}
