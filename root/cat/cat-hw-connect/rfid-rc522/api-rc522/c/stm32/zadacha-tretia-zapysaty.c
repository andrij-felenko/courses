// Записати 16 байтів у блок і перечитати назад для перевірки.
HAL_StatusTypeDef write_and_verify(uint8_t block, const uint8_t *data16) {
    if (pcd_authenticate(0x60, block) != HAL_OK) return HAL_ERROR;  // auth як для читання

    // --- ЗАПИС: MIFARE Write іде у ДВА прийоми, на кожен мітка відповідає ACK (0x0A) ---
    uint8_t hdr[2] = { 0xA0, block };                  // 1) «готуйся писати в цей блок»
    if (picc_mf_command(hdr, 2) != HAL_OK) {
        printf("Write: мітка не прийняла адресу\r\n");
        return HAL_ERROR;
    }
    if (picc_mf_command(data16, 16) != HAL_OK) {       // 2) рівно 16 Б (не 18! CRC — чип)
        printf("Write провалився\r\n");
        return HAL_ERROR;
    }
    printf("Записано.\r\n");

    // --- Перечитуємо назад для впевненості ---
    uint8_t cmd[2] = { 0x30, block };
    uint8_t buf[18]; uint8_t n = sizeof(buf);
    if (picc_transceive_crc(cmd, 2, buf, &n) == HAL_OK) {
        printf("Перечитано:");
        for (uint8_t i = 0; i < 16; i++) printf(" %02X", buf[i]);
        printf("\r\n");
    }

    // ОБОВ'ЯЗКОВИЙ фінал сесії з міткою:
    picc_halta();                                      // 1. відпустити мітку (HLTA)
    pcd_write(REG_STATUS2, pcd_read(REG_STATUS2) & ~0x08);   // 2. скинути MFCrypto1On
    return HAL_OK;
}
