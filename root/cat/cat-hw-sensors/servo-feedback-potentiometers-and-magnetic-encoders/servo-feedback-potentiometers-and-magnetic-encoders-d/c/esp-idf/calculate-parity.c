// Зчитування магнітного енкодера через SPI та перевірка парності у C (ESP-IDF)
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "driver/spi_master.h"

#define ANGLE_REG           0x3FFF // Адреса регістра кута (на прикладі AS5048)
#define READ_CMD_FLAG       0x4000 // Біт читання
#define PARITY_MASK         0x8000 // Біт парності

// Обчислення парності 16-бітного слова (парне число одиниць -> 0, непарне -> 1)
static bool calculate_parity(uint16_t val) {
    uint16_t cnt = 0;
    for (int i = 0; i < 16; i++) {
        if (val & (1 << i)) cnt++;
    }
    return (cnt % 2) != 0;
}

// Зчитування 14-бітного кута в градусах (0.0° - 360.0°)
float read_magnetic_encoder_angle_spi(spi_device_handle_t spi) {
    uint16_t cmd = ANGLE_REG | READ_CMD_FLAG;
    if (calculate_parity(cmd)) {
        cmd |= PARITY_MASK;
    }

    spi_transaction_t t = {
        .length = 16,
        .tx_buffer = &cmd,
        .flags = SPI_TRANS_USE_RXDATA,
    };

    esp_err_t ret = spi_device_transmit(spi, &t);
    if (ret != ESP_OK) return -1.0f;

    uint16_t rx_data = (t.rx_data[0] << 8) | t.rx_data[1];

    // Перевірка цілісності кадру за бітом парності
    if (calculate_parity(rx_data & 0x7FFF) != ((rx_data & PARITY_MASK) >> 15)) {
        return -1.0f; // Помилка парності кадру
    }

    uint16_t raw_angle = rx_data & 0x3FFF; // Виділення 14-бітного значення
    return ((float)raw_angle * 360.0f) / 16384.0f;
}
