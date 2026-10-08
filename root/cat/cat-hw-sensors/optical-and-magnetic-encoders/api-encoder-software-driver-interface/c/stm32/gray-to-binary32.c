uint32_t gray_to_binary32(uint32_t gray) {
    uint32_t binary = gray;
    binary ^= (binary >> 1);
    binary ^= (binary >> 2);
    binary ^= (binary >> 4);
    binary ^= (binary >> 8);
    binary ^= (binary >> 16);
    return binary;
}

void encoder_decode_ssi_frame(encoder_driver_t *drv, uint32_t raw_ssi_frame) {
    uint32_t gray_pos = (raw_ssi_frame >> 1) & 0x0FFF; // Виділення 12 бітів позиції
    uint32_t binary_pos = gray_to_binary32(gray_pos);
    drv->raw_counter = (int32_t)binary_pos;
}
