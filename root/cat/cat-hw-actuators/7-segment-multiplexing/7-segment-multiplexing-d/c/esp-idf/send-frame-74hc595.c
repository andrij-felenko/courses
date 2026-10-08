// Передача сегментної маски та коду розряду у дворегістрову каскадну схему 74HC595 (C / ESP-IDF)
#include <stdint.h>
#include "driver/spi_master.h"

extern spi_device_handle_t display_spi;

void send_frame_74hc595(uint8_t segment_mask, uint8_t digit_select_mask) {
    uint8_t tx_data[2];
    // Спочатку відправляємо маску розряду, потім маску сегментів (залежно від порядку в каскаді)
    tx_data[0] = digit_select_mask;
    tx_data[1] = segment_mask;

    spi_transaction_t t = {
        .length = 16, // 16 біт для двох регістрів
        .tx_buffer = tx_data,
    };
    
    // Апаратна передача через SPI
    spi_device_transmit(display_spi, &t);
}
