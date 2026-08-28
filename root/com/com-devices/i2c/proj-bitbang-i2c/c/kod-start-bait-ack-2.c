/* Записати номер регістра, повторний START, прочитати n байт. */
bool i2c_read_reg(uint8_t addr7, uint8_t reg, uint8_t *buf, uint8_t n) {
    i2c_fault = false;
    if (!i2c_start())                                 goto fail;
    if (!i2c_write_byte((uint8_t)((addr7 << 1) | 0))) goto fail;  /* R/W = 0: запис */
    if (!i2c_write_byte(reg))                         goto fail;
    if (!i2c_start())                                 goto fail;  /* повторний START */
    if (!i2c_write_byte((uint8_t)((addr7 << 1) | 1))) goto fail;  /* R/W = 1: читання */
    for (uint8_t i = 0; i < n; i++)
        buf[i] = i2c_read_byte((uint8_t)(i + 1) < n); /* останньому — NACK */
    i2c_stop();
    return !i2c_fault;
fail:
    i2c_stop();             /* хоч би що сталося — звільнити шину */
    return false;
}
