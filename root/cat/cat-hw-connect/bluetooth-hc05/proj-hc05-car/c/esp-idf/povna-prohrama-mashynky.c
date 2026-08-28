#include <stdio.h>
#include <stdbool.h>
#include "driver/uart.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_timer.h"
#include "esp_log.h"

#define BT_UART    UART_NUM_2
#define PIN_TXD    GPIO_NUM_17      // → RXD модуля (3.3 В — дільник не потрібен)
#define PIN_RXD    GPIO_NUM_16      // ← TXD модуля
#define PIN_STATE  GPIO_NUM_4

static const char *TAG = "car";

static int      speedLevel    = 5;
static bool     wasConnected  = false;
static int64_t  lastTelemetry = 0;

void  applyDrive(int leftDir, int rightDir);   // ваша реалізація моторів
float readBattery(void);                       // ваш давач напруги

static void handleCommand(char c) {
    switch (c) {
        case 'F': applyDrive(+1, +1); break;
        case 'B': applyDrive(-1, -1); break;
        case 'L': applyDrive(-1, +1); break;
        case 'R': applyDrive(+1, -1); break;
        case 'S': applyDrive( 0,  0); break;
        default:
            if (c >= '0' && c <= '9') speedLevel = c - '0';
            break;
    }
}

static void btInit(void) {
    const uart_config_t cfg = {
        .baud_rate  = 9600,          // РОБОЧА швидкість модуля (не 38400 — тут не AT)
        .data_bits  = UART_DATA_8_BITS,
        .parity     = UART_PARITY_DISABLE,
        .stop_bits  = UART_STOP_BITS_1,
        .flow_ctrl  = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT,
    };
    ESP_ERROR_CHECK(uart_driver_install(BT_UART, 256, 0, 0, NULL, 0));
    ESP_ERROR_CHECK(uart_param_config(BT_UART, &cfg));
    ESP_ERROR_CHECK(uart_set_pin(BT_UART, PIN_TXD, PIN_RXD,
                                 UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE));

    gpio_config_t st = {
        .pin_bit_mask = 1ULL << PIN_STATE,
        .mode         = GPIO_MODE_INPUT,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&st));
}

void app_main(void) {
    btInit();
    applyDrive(0, 0);                // старт зі стопу

    while (1) {
        // 1) команди від телефона → дії; 0 тиків очікування = НЕ блокуємось
        uint8_t buf[32];
        int n = uart_read_bytes(BT_UART, buf, sizeof buf, 0);
        for (int i = 0; i < n; i++) handleCommand((char)buf[i]);

        // 2) сторож зв'язку: обрив → аварійний стоп
        bool connected = gpio_get_level(PIN_STATE);
        if (wasConnected && !connected) {
            applyDrive(0, 0);
            ESP_LOGW(TAG, "Зв'язок втрачено — стоп.");
        }
        wasConnected = connected;

        // 3) телеметрія раз на секунду, без блокування
        int64_t now = esp_timer_get_time() / 1000;   // мкс → мс
        if (connected && now - lastTelemetry >= 1000) {
            lastTelemetry = now;
            char line[32];
            int len = snprintf(line, sizeof line, "BAT:%.2f SPD:%d\r\n",
                               readBattery(), speedLevel);
            uart_write_bytes(BT_UART, line, len);
        }

        vTaskDelay(pdMS_TO_TICKS(5));   // віддаємо процесор іншим задачам RTOS
    }
}
