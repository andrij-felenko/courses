// Зчитати 14-бітовий кут з магнітного енкодера через SPI
#include "driver/spi_master.h"
#include <stdint.h>
#include <stdbool.h>

uint16_t read_encoder_angle_spi(spi_device_handle_t spi) {
    uint8_t tx_data[2] = {0xFF, 0xFF}; // Команда читання кута
    uint8_t rx_data[2] = {0};
    
    spi_transaction_t t = {
        .length = 16,
        .tx_buffer = tx_data,
        .rx_buffer = rx_data,
    };
    
    if (spi_device_transmit(spi, &t) == ESP_OK) {
        uint16_t raw_val = ((uint16_t)rx_data[0] << 8) | rx_data[1];
        // Перевірка парності (простий контроль цілісності)
        uint16_t parity = 0;
        for (uint16_t temp = raw_val; temp > 0; temp >>= 1) {
            parity ^= (temp & 1);
        }
        if (parity == 0) { // Парність збігається
            return raw_val & 0x3FFF; // Повертаємо 14 біт кута
        }
    }
    return 0xFFFF; // Помилка зчитування
}
