// Запис у NTAG I2C Plus починаючи з адреси блоку user memory (0x04)
ndef_status_t nfc_tag_write_ndef(uint8_t i2c_addr_7bit, 
                                 const uint8_t *ndef_raw, 
                                 size_t ndef_len,
                                 bool (*i2c_write_fn)(uint8_t addr, uint8_t mem_addr, const uint8_t *data, size_t len)) {
    if (!ndef_raw || ndef_len == 0 || !i2c_write_fn) return NDEF_ERR_INVALID_PARAM;
    
    // Формуємо образ памяті з TLV структурою
    uint8_t memory_image[256];
    size_t offset = 0;
    
    // Capability Container (CC) для NTAG I2C (блок 0x03) зазвичай уже прошитий.
    // Починаємо формувати NDEF TLV:
    memory_image[offset++] = 0x03; // NDEF TLV Marker
    if (ndef_len < 255) {
        memory_image[offset++] = (uint8_t)ndef_len;
    } else {
        memory_image[offset++] = 0xFF;
        memory_image[offset++] = (uint8_t)(ndef_len >> 8);
        memory_image[offset++] = (uint8_t)(ndef_len & 0xFF);
    }
    
    memcpy(&memory_image[offset], ndef_raw, ndef_len);
    offset += ndef_len;
    memory_image[offset++] = 0xFE; // Terminator TLV
    
    // Запис сторінками по 16 байтів у пам'ять мітки
    uint8_t start_block = 0x04; // Перший блок користувацької EEPROM
    size_t bytes_written = 0;
    
    while (bytes_written < offset) {
        size_t chunk = offset - bytes_written;
        if (chunk > 16) chunk = 16;
        
        uint8_t page_buf[16] = {0};
        memcpy(page_buf, &memory_image[bytes_written], chunk);
        
        if (!i2c_write_fn(i2c_addr_7bit, start_block, page_buf, 16)) {
            return NDEF_ERR_I2C_FAULT;
        }
        
        start_block++;
        bytes_written += chunk;
    }
    
    return NDEF_OK;
}
