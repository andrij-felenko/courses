float asa[3];   // заводські множники осей, заповнить ak_read_asa()

void ak_init_bypass(void) {
    if (read_u8(AK_ADDR, AK_WIA) != 0x48) return;   // паспорт магнетометра

    // Читаємо ASA (потрібно зайти в режим Fuse ROM), потім вмикаємо вимір.
    ak_read_asa();                                  // див. наступний розділ
    i2c_write_reg(AK_ADDR, AK_CNTL1, AK_MODE_CONT2_16B);
    delay_ms(10);
}
