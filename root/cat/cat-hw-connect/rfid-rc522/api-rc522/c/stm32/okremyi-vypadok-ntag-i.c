// Читання NTAG/Ultralight: сторінки по 4 байти, БЕЗ автентифікації.
// READ (0x30) віддає 4 сторінки за раз (16 байтів у 18-байтовий буфер).
HAL_StatusTypeDef read_ntag_page(uint8_t page) {
    uint8_t cmd[2] = { 0x30, page };     // ніякого MFAuthent — читання NTAG відкрите
    uint8_t buf[18]; uint8_t n = sizeof(buf);
    if (picc_transceive_crc(cmd, 2, buf, &n) != HAL_OK) {
        printf("NTAG read провалився\r\n");
        return HAL_ERROR;
    }
    // buf[0..15] = сторінки page, page+1, page+2, page+3 (по 4 байти)
    for (uint8_t p = 0; p < 4; p++)
        printf("Сторінка %d: %02X %02X %02X %02X\r\n", page + p,
               buf[p * 4], buf[p * 4 + 1], buf[p * 4 + 2], buf[p * 4 + 3]);
    return HAL_OK;
}
