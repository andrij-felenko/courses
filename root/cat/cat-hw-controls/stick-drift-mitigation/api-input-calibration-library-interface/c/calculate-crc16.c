static uint16_t calculate_crc16(const uint8_t *data, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; ++j) {
            if (crc & 0x0001) {
                crc = (crc >> 1) ^ 0xA001;
            } else {
                crc >>= 1;
            }
        }
    }
    return crc;
}

input_error_t input_profile_save(input_profile_t *profile, uint32_t nvm_address) {
    if (profile == NULL) {
        return INPUT_ERR_INVALID_PARAM;
    }
    size_t payload_len = sizeof(input_profile_t) - sizeof(uint16_t);
    profile->crc16 = calculate_crc16((const uint8_t *)profile, payload_len);
    return INPUT_OK;
}

input_error_t input_profile_load(input_profile_t *profile, uint32_t nvm_address) {
    if (profile == NULL) {
        return INPUT_ERR_INVALID_PARAM;
    }
    size_t payload_len = sizeof(input_profile_t) - sizeof(uint16_t);
    uint16_t expected_crc = calculate_crc16((const uint8_t *)profile, payload_len);
    if (profile->crc16 != expected_crc) {
        return INPUT_ERR_CRC_MISMATCH;
    }
    return INPUT_OK;
}
