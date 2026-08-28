void ak_read_asa(void) {
    uint8_t raw[3];
    // 1. Спершу — power-down (перемикати режими можна лише через нього).
    i2c_write_reg(AK_ADDR, AK_CNTL1, AK_MODE_POWERDOWN);
    delay_ms(10);
    // 2. Режим доступу до заводської пам'яті.
    i2c_write_reg(AK_ADDR, AK_CNTL1, AK_MODE_FUSEROM);
    delay_ms(10);
    // 3. Три байти поправок поспіль (ASAX, ASAY, ASAZ = 0x10..0x12).
    i2c_read_regs(AK_ADDR, AK_ASAX, raw, 3);
    // 4. Назад у power-down (перед вмиканням вимірювального режиму).
    i2c_write_reg(AK_ADDR, AK_CNTL1, AK_MODE_POWERDOWN);
    delay_ms(10);

    // Перерахунок у множник. Формула з datasheet AK8963:
    //   adj = ((ASA - 128) * 0.5 / 128) + 1  =  ((ASA - 128) / 256) + 1
    for (int i = 0; i < 3; i++)
        asa[i] = ((float)(raw[i] - 128) / 256.0f) + 1.0f;
}
