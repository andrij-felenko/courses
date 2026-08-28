#define REG_I2C_MST_CTRL    0x24
#define REG_I2C_SLV0_ADDR   0x25       // адреса слейва (+ біт READ = 0x80)
#define REG_I2C_SLV0_REG    0x26       // з якого регістра слейва починати
#define REG_I2C_SLV0_CTRL   0x27       // біт EN (0x80) + кількість байтів
#define REG_EXT_SENS_DATA_00 0x49      // сюди майстер складає прочитане

// Спершу магнетометр треба ОДИН РАЗ налаштувати. Для цього — короткочасно
// підняти bypass, увімкнути безперервний режим AK, прочитати ASA, і лише
// потім віддати AK8963 внутрішньому майстрові.
void ak_init_slave(void) {
    ak_enable_bypass();                             // тимчасово відкриваємо прохід
    if (read_u8(AK_ADDR, AK_WIA) != 0x48) return;
    ak_read_asa();                                  // заводські поправки
    i2c_write_reg(AK_ADDR, AK_CNTL1, AK_MODE_CONT2_16B);
    delay_ms(10);

    // Тепер закриваємо bypass і піднімаємо внутрішній майстер MPU.
    i2c_write_reg(MPU_ADDR, REG_INT_PIN_CFG, 0x00); // BYPASS_EN → 0
    i2c_write_reg(MPU_ADDR, REG_USER_CTRL,   0x20); // I2C_MST_EN (біт 5)
    i2c_write_reg(MPU_ADDR, REG_I2C_MST_CTRL, 0x0D);// такт внутр. шини ~400 кГц
    delay_ms(3);

    // Навчаємо слейв 0: читати AK8963, 7 байтів, з регістра ST1.
    i2c_write_reg(MPU_ADDR, REG_I2C_SLV0_ADDR, AK_ADDR | 0x80); // 0x80 = READ
    i2c_write_reg(MPU_ADDR, REG_I2C_SLV0_REG,  AK_ST1);
    i2c_write_reg(MPU_ADDR, REG_I2C_SLV0_CTRL, 0x80 | 7);       // EN + 7 байтів
    delay_ms(3);
}
