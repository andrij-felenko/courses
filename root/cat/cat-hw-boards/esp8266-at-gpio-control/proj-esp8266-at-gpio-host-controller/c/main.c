#include <stdio.h>
#include <stdbool.h>
#include "esp8266_at_gpio.h"

// Симуляція передачі байтів у фізичний UART
static void hardware_uart_send(uint8_t byte) {
    putchar((char)byte);
}

// Обробник асинхронних URC сповіщень про зміну стану входу GPIO
static void on_gpio_interrupt(uint8_t pin, uint8_t value) {
    printf("\n[URC EVENT] Зміна стану на GPIO%d -> Новий рівень: %d\n", pin, value);
}

int main(void) {
    esp8266_driver_t esp_driver;
    esp8266_init(&esp_driver, hardware_uart_send, on_gpio_interrupt);

    printf("Ініціалізація неблокуючого драйвера ESP8266 AT GPIO...\n");

    // Крок 1: Конфігурація GPIO12 як виходу
    printf("\n--- Відправка команди AT+SYSGPIODIR=12,1 ---\n");
    esp8266_set_gpio_mode(&esp_driver, 12, GPIO_MODE_OUTPUT);

    // Симуляція отримання відповіді "OK\r\n" від модуля через UART
    const char *simulated_ok = "OK\r\n";
    for (int i = 0; simulated_ok[i] != '\0'; i++) {
        esp8266_process_rx_byte(&esp_driver, simulated_ok[i]);
    }

    // Крок 2: Запис HIGH на GPIO12
    if (esp_driver.state == ESP_STATE_IDLE) {
        printf("\n--- Відправка команди AT+SYSGPIOWRITE=12,1 ---\n");
        esp8266_write_gpio(&esp_driver, 12, 1);
        for (int i = 0; simulated_ok[i] != '\0'; i++) {
            esp8266_process_rx_byte(&esp_driver, simulated_ok[i]);
        }
    }

    // Крок 3: Симуляція надходження асинхронного URC сповіщення про переривання на GPIO4
    printf("\n--- Симуляція асинхронного URC (+GPIO_INT:4,1) ---\n");
    const char *simulated_urc = "+GPIO_INT:4,1\r\n";
    for (int i = 0; simulated_urc[i] != '\0'; i++) {
        esp8266_process_rx_byte(&esp_driver, simulated_urc[i]);
    }

    // Неблокуючий демонстраційний цикл
    uint32_t simulated_time = 0;
    while (simulated_time < 500) {
        esp8266_update_tick(&esp_driver, 10);
        simulated_time += 10;
    }

    printf("\nДемонстрацію роботи FSM драйвера успішно завершено.\n");
    return 0;
}
