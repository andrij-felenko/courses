// Прочитати слот #i. Повертає 1, якщо слот ДІЙСНИЙ (сума збіглася), інакше 0.
// При успіху заповнює *seq (послідовність) і копіює WL_DATA_LEN байтів у data.
static int wl_read_slot(uint16_t i, uint32_t *seq, uint8_t *data) {
    uint8_t buf[WL_SLOT_LEN];
    eeprom_read(WL_BASE + i * WL_SLOT_LEN, buf, WL_SLOT_LEN);

    // Контрольна сума слота — останній байт; рахуємо її з усього, що перед нею.
    uint8_t want = buf[WL_SLOT_LEN - 1];
    uint8_t got  = crc8(buf, WL_SLOT_LEN - WL_CRC_LEN);
    if (got != want) return 0;                 // покруч: недописаний або вигорілий

    // Послідовність лежить одразу за даними (порядок байтів — молодший першим).
    uint32_t s = (uint32_t)buf[WL_DATA_LEN]
               | (uint32_t)buf[WL_DATA_LEN + 1] << 8
               | (uint32_t)buf[WL_DATA_LEN + 2] << 16
               | (uint32_t)buf[WL_DATA_LEN + 3] << 24;

    // seq == 0 — домовленість «слот ніколи не писався»: перший запис почнемо з 1,
    // тож 0 у дійсному слоті означати не може (порожня EEPROM усе одно впаде на CRC).
    if (s == 0) return 0;

    *seq = s;
    memcpy(data, buf, WL_DATA_LEN);
    return 1;
}
