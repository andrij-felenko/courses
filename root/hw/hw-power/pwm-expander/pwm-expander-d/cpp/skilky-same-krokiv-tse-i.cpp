// Записати шпаруватість каналу (0..4095) у PWM-розширювач по I2C.
// reg_base — адреса першого регістра ON цього каналу; OFF іде за двома
// байтами ON. У поширеній мікросхемі регістри йдуть четвірками:
// ON_L, ON_H, OFF_L, OFF_H — по 4 на канал.
void pwm_set_duty(uint8_t ch, uint16_t off_count) {
    uint8_t reg = 0x06 + 4 * ch;            // база регістрів каналу ch
    uint8_t buf[5] = {
        reg,
        0x00, 0x00,                          // ON = 0  (вмикаємось на початку)
        (uint8_t)(off_count & 0xFF),         // OFF молодший байт
        (uint8_t)(off_count >> 8)            // OFF старший байт (лише 4 біти значущі)
    };
    i2c_write(EXPANDER_ADDR, buf, sizeof buf);
}

// 40 % на каналі 5:
pwm_set_duty(5, (uint16_t)(0.40f * 4096));   // → 1638
