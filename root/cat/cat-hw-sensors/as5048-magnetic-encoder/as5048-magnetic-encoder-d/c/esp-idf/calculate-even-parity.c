#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "driver/spi_master.h"

// Обчислення парної парності (even parity) для 16-бітного слова
static bool calculate_even_parity(uint16_t value) {
    uint16_t count = 0;
    for (int i = 0; i < 16; i++) {
        if (value & (1 << i)) {
            count++;
        }
    }
    return (count % 2) != 0; // повертає true, якщо треба додати 1 для парності
}

// Формування SPI-кадру для зчитування регістра AS5048A
uint16_t as5048a_make_read_frame(uint16_t address) {
    uint16_t frame = 0x4000 | (address & 0x3FFF); // Bit 14 = 1 (Read)
    if (calculate_even_parity(frame)) {
        frame |= 0x8000; // Bit 15 = Parity
    }
    return frame;
}

// Зчитування 14-бітного кута з урахуванням затримки конвеєра на один кадр
esp_err_t as5048a_read_angle(spi_device_handle_t spi, uint16_t *angle_out) {
    uint16_t command = as5048a_make_read_frame(0x3FFE); // Регістр ANGLE
    spi_transaction_t t = {
        .flags = SPI_TRANS_USE_RXDATA | SPI_TRANS_USE_TXDATA,
        .length = 16,
        .tx_data = { (command >> 8) & 0xFF, command & 0xFF },
    };

    // Відправка запиту каду N
    esp_err_t ret = spi_device_transmit(spi, &t);
    if (ret != ESP_OK) return ret;

    // Відправка другого каду (NOP) для отримання відповіді каду N
    ret = spi_device_transmit(spi, &t);
    if (ret != ESP_OK) return ret;

    uint16_t rx_frame = (t.rx_data[0] << 8) | t.rx_data[1];

    // Перевірка прапорця помилки (Bit 14)
    if (rx_frame & 0x4000) {
        return ESP_FAIL; // Виникла помилка в сенсорі
    }

    *angle_out = rx_frame & 0x3FFF; // 14-бітне значення кута
    return ESP_OK;
}
