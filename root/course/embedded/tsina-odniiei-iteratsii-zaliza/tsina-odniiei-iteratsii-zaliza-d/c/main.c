#include "driver/uart.h"
#include "driver/gpio.h"
#include "esp_err.h"

#define UART_PORT_NUM      UART_NUM_1
#define UART_BAUD_RATE     115200

/* Апаратна помилка на платі Rev A:
 * Очікувалося: GPIO17 = TX, GPIO18 = RX
 * Фізично підведено: GPIO17 = RX зовнішнього чипа, GPIO18 = TX зовнішнього чипа
 */
#define REV_A_HW_TX_PIN    GPIO_NUM_18  /* Програмний ремапінг: призначаємо TX на пін 18 */
#define REV_A_HW_RX_PIN    GPIO_NUM_17  /* Програмний ремапінг: призначаємо RX на пін 17 */

esp_err_t init_uart_with_hw_fix(void) {
    uart_config_t uart_config = {
        .baud_rate = UART_BAUD_RATE,
        .data_bits = UART_DATA_8_BITS,
        .parity    = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT,
    };

    esp_err_t err = uart_param_config(UART_PORT_NUM, &uart_config);
    if (err != ESP_OK) return err;

    /* Використовуємо внутрішню матрицю GPIO Matrix для обходу помилки трасування */
    err = uart_set_pin(UART_PORT_NUM, 
                       REV_A_HW_TX_PIN, 
                       REV_A_HW_RX_PIN, 
                       UART_PIN_NO_CHANGE, 
                       UART_PIN_NO_CHANGE);
    if (err != ESP_OK) return err;

    const int rx_buffer_size = 1024;
    return uart_driver_install(UART_PORT_NUM, rx_buffer_size, 0, 0, NULL, 0);
}
