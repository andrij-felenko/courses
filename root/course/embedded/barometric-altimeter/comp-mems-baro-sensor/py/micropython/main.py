# Перше знайомство з MEMS-барометром: від упізнання до тиску в паскалях.
# i2c — шина machine.I2C; readfrom_mem/writeto_mem абстрагують доступ до регістрів.
# _read_calibration повертає коефіцієнти; _compensate_pressure проганяє сирі коди.

class Barometer:
    def __init__(self, i2c, addr=0x76):
        self._i2c = i2c
        self._addr = addr
        self._cal = None

    def init(self):
        # 1) упізнати чип за фіксованим підписом
        if self._reg(REG_CHIP_ID) != EXPECTED_CHIP_ID:
            return False                            # не той чип / мертва шина

        # 2) один раз вичитати заводські коефіцієнти в пам'ять МК
        self._cal = self._read_calibration()        # блок з ПЗП -> RAM

        # 3) налаштувати передискретизацію (тиск точніше за температуру) і режим
        self._reg(REG_OSR, OSR_P_x16 | OSR_T_x2)    # важке усереднення на p
        self._reg(REG_MODE, MODE_NORMAL | ODR_50HZ)
        return True

    def read_pressure(self):
        # 4) переконатися, що вимір свіжий
        if not (self._reg(REG_STATUS) & STATUS_DATA_READY):
            return None

        # 5) забрати сирі коди: СПОЧАТКУ температура, ПОТІМ тиск (порядок важливий)
        raw_t = self._read24(REG_TEMP_RAW)          # 3 байти, 24 біти
        raw_p = self._read24(REG_PRESS_RAW)

        # 6) компенсація: сирі коди + коефіцієнти -> справжній тиск, Pa
        return self._compensate_pressure(raw_t, raw_p, self._cal)

    def _reg(self, reg, value=None):
        if value is None:
            return self._i2c.readfrom_mem(self._addr, reg, 1)[0]
        self._i2c.writeto_mem(self._addr, reg, bytes([value]))

    def _read24(self, reg):
        b = self._i2c.readfrom_mem(self._addr, reg, 3)
        return (b[0] << 16) | (b[1] << 8) | b[2]
