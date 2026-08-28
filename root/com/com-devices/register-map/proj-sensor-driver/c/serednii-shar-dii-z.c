// перевірити, що на шині справді MPU-6050
bool mpu_present(void) {
    uint8_t id = 0;
    if (mpu_read(REG_WHO, &id, 1) != MPU_OK) return false;
    return id == 0x68;                       // сталий код саме цього чіпа
}

// розбудити чіп і виставити діапазон ±8g (AFS = 0b10 у бітах 4:3)
uint8_t mpu_begin(void) {
    uint8_t err = mpu_write(REG_PWR, 0x00);  // вийти зі сну
    if (err) return err;
    uint8_t cfg = 0;
    err = mpu_read(REG_CFG, &cfg, 1);        // читай…
    if (err) return err;
    cfg = (cfg & ~0x18) | (0b10 << 3);       // …зміни поле AFS…
    return mpu_write(REG_CFG, cfg);          // …запиши
}
