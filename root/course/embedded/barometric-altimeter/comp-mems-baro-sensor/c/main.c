// Перше знайомство з MEMS-барометром: від упізнання до тиску в паскалях.
// Функції bus_read/bus_write абстрагують шину (I2C чи SPI — байдуже нижчому шару).
// cal_t — структура коефіцієнтів; compensate_pressure проганяє сирі коди через них.

bool baro_init(baro_t *dev) {
    // 1) упізнати чип за фіксованим підписом
    uint8_t id = bus_read(dev, REG_CHIP_ID);
    if (id != EXPECTED_CHIP_ID) return false;      // не той чип / мертва шина

    // 2) один раз вичитати заводські коефіцієнти в пам'ять МК
    read_calibration(dev, &dev->cal);              // блок з ПЗП -> RAM

    // 3) налаштувати передискретизацію (тиск точніше за температуру) і режим
    bus_write(dev, REG_OSR, OSR_P_x16 | OSR_T_x2); // важке усереднення на p
    bus_write(dev, REG_MODE, MODE_NORMAL | ODR_50HZ);
    return true;
}

bool baro_read_pressure(baro_t *dev, float *pa) {
    // 4) переконатися, що вимір свіжий
    if (!(bus_read(dev, REG_STATUS) & STATUS_DATA_READY)) return false;

    // 5) забрати сирі коди: СПОЧАТКУ температура, ПОТІМ тиск (порядок важливий)
    int32_t raw_t = read24(dev, REG_TEMP_RAW);     // 3 байти, 24 біти
    int32_t raw_p = read24(dev, REG_PRESS_RAW);

    // 6) компенсація: сирі коди + коефіцієнти -> справжній тиск, Pa
    *pa = compensate_pressure(raw_t, raw_p, &dev->cal);
    return true;
}
