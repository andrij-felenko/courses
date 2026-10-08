#include <stdint.h>
#include <stdbool.h>
#include "driver/spi_master.h"

#define AS5048_CMD_READ_ANGLE 0xFFFF
#define AS5048_CMD_NOP        0x0000

static bool calculate_even_parity(uint16_t value) {
    uint16_t count = 0;
    for (int i = 0; i < 16; i++) {
        if ((value >> i) & 0x01) count++;
    }
    return (count % 2) == 0;
}

bool as5048_spi_read_angle(spi_device_handle_t spi, float *angle_deg) {
    spi_transaction_t t1 = {
        .flags = SPI_TRANS_USE_RXDATA | SPI_TRANS_USE_TXDATA,
        .length = 16,
        .tx_data = { (AS5048_CMD_READ_ANGLE >> 8) & 0xFF, AS5048_CMD_READ_ANGLE & 0xFF }
    };
    
    // Крок 1: Надсилання запиту на зчитування кута (відповідь MISO містить старі дані)
    if (spi_device_transmit(spi, &t1) != ESP_OK) return false;

    spi_transaction_t t2 = {
        .flags = SPI_TRANS_USE_RXDATA | SPI_TRANS_USE_TXDATA,
        .length = 16,
        .tx_data = { (AS5048_CMD_NOP >> 8) & 0xFF, AS5048_CMD_NOP & 0xFF }
    };

    // Крок 2: Виштовхування відповіді з даними кута через команду NOP
    if (spi_device_transmit(spi, &t2) != ESP_OK) return false;

    uint16_t miso_frame = ((uint16_t)t2.rx_data[0] << 8) | t2.rx_data[1];

    // Перевірка цілісності кадру за контролем парності
    if (!calculate_even_parity(miso_frame)) {
        return false; // Помилка парності кадру
    }

    // Перевірка прапорця апаратної помилки (Біт 14)
    if (miso_frame & (1 << 14)) {
        return false; // Зафіксовано апаратну помилку в енкодері
    }

    uint16_t raw_angle = miso_frame & 0x3FFF;
    *angle_deg = ((float)raw_angle * 360.0f) / 16384.0f;
    return true;
}
