#define ENCODER_ERR_NONE       0x00
#define ENCODER_ERR_CRC        0x01
#define ENCODER_ERR_TRANSITION 0x02
#define ENCODER_ERR_TIMEOUT    0x04

uint8_t calculate_biss_crc6(uint32_t data, uint8_t bit_count) {
    uint8_t crc = 0x00; // Початковий залишок
    for (int i = bit_count - 1; i >= 0; i--) {
        uint8_t bit = (data >> i) & 0x01;
        if (((crc >> 5) ^ bit) & 0x01) {
            crc = ((crc << 1) ^ 0x43) & 0x3F;
        } else {
            crc = (crc << 1) & 0x3F;
        }
    }
    return crc ^ 0x3F; // Інверсія результату
}

void encoder_dma_rx_callback(encoder_driver_t *drv, uint32_t raw_data, uint8_t rx_crc) {
    uint8_t calc_crc = calculate_biss_crc6(raw_data, 24);
    if (calc_crc != rx_crc) {
        drv->error_flags |= ENCODER_ERR_CRC;
        return;
    }
    drv->error_flags &= ~ENCODER_ERR_CRC;
    // Оновлення позиції після успішної перевірки
}
