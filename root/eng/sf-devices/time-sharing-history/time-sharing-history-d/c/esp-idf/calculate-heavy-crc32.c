#include <stdio.h>
#include <stdint.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/uart.h"

#define BUF_SIZE (1024)

// Монолітна обчислювальна задача, що блокує процесорне ядро
uint32_t calculate_heavy_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 1) {
                crc = (crc >> 1) ^ 0xEDB88320;
            } else {
                crc >>= 1;
            }
            // Штучна затримка для імітації обробки великого масиву
            esp_rom_delay_us(10);
        }
    }
    return ~crc;
}

void app_main(void) {
    uint8_t buffer[BUF_SIZE];
    
    // Ініціалізація даних
    for (int i = 0; i < BUF_SIZE; i++) buffer[i] = (uint8_t)i;

    while (1) {
        // Запуск тривалого обчислення: процесор заблокований приблизно на 80 мс
        uint32_t crc = calculate_heavy_crc32(buffer, BUF_SIZE);
        (void)crc;

        // Лише після завершення обчислення прошивка намагається перевірити UART
        // За цей час апаратний FIFO переповнюється і байти втрачаються
        uint8_t rx_data[64];
        int len = uart_read_bytes(UART_NUM_0, rx_data, sizeof(rx_data), 0);
        if (len > 0) {
            // Обробка прийнятих даних (виконується із величезним запізненням)
        }
    }
}
