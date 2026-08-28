#include "driver/uart.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "esp_log.h"
#include "esp_timer.h"

static const char *TAG = "app";
#define LED GPIO_NUM_2

void app_main(void) {
    const uart_config_t cfg = {
        .baud_rate  = 9600,             // 9600 бод — обидва боки мусять збігтися
        .data_bits  = UART_DATA_8_BITS,
        .parity     = UART_PARITY_DISABLE,
        .stop_bits  = UART_STOP_BITS_1,
        .flow_ctrl  = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT,
    };
    ESP_ERROR_CHECK(uart_driver_install(UART_NUM_0, 256, 0, 0, NULL, 0));
    ESP_ERROR_CHECK(uart_param_config(UART_NUM_0, &cfg));
    gpio_set_direction(LED, GPIO_MODE_OUTPUT);
    ESP_LOGI(TAG, "Готовий");           // сталі рядки й так лежать у флеші

    int64_t last = 0;
    while (1) {
        uint8_t cmd;                    // приймання: одна літера-команда
        if (uart_read_bytes(UART_NUM_0, &cmd, 1, pdMS_TO_TICKS(10)) == 1) {
            if (cmd == '1') gpio_set_level(LED, 1);
            if (cmd == '0') gpio_set_level(LED, 0);
        }
        int64_t now = esp_timer_get_time();   // мікросекунди від старту
        if (now - last >= 1000000) {          // передавання: показник щосекунди
            last = now;
            ESP_LOGI(TAG, "лічильник = %d", (int)(now / 1000000));
        }
    }
}
