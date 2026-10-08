#include <stdint.h>
#include <stdbool.h>
#include "driver/spi_master.h"

typedef struct {
    bool magnetic_too_weak;  // COMP_LOW
    bool magnetic_too_strong;// COMP_HIGH
    bool cordic_overflow;    // COF
    bool offset_comp_done;   // OCF
    uint8_t agc_gain;        // Коефіцієнт підсилення AGC (0..255)
} as5048_diag_status_t;

#define AS5048_CMD_READ_DIAG 0x7FFD // Адреса регістру 0x3FFD з прапорцем читання та парності

bool as5048_read_diagnostics(spi_device_handle_t spi, as5048_diag_status_t *status) {
    spi_transaction_t t1 = {
        .flags = SPI_TRANS_USE_RXDATA | SPI_TRANS_USE_TXDATA,
        .length = 16,
        .tx_data = { (AS5048_CMD_READ_DIAG >> 8) & 0xFF, AS5048_CMD_READ_DIAG & 0xFF }
    };
    if (spi_device_transmit(spi, &t1) != ESP_OK) return false;

    spi_transaction_t t2 = {
        .flags = SPI_TRANS_USE_RXDATA | SPI_TRANS_USE_TXDATA,
        .length = 16,
        .tx_data = { 0x00, 0x00 } // NOP
    };
    if (spi_device_transmit(spi, &t2) != ESP_OK) return false;

    uint16_t miso = ((uint16_t)t2.rx_data[0] << 8) | t2.rx_data[1];

    status->agc_gain         = miso & 0xFF;            // Біти [7:0]
    status->offset_comp_done = (miso & (1 << 10)) != 0;// Біт 10 (OCF)
    status->cordic_overflow  = (miso & (1 << 11)) != 0;// Біт 11 (COF)
    status->magnetic_too_weak= (miso & (1 << 12)) != 0;// Біт 12 (COMP_LOW)
    status->magnetic_too_strong=(miso & (1 << 13)) != 0;// Біт 13 (COMP_HIGH)

    // Аварійний стан при відсутності або насиченні поля
    if (status->magnetic_too_weak || status->magnetic_too_strong || status->cordic_overflow) {
        return false;
    }
    return true;
}
