// Перше знайомство з MEMS-барометром: від упізнання до тиску в паскалях.
// Bus — абстракція шини (I2C чи SPI): методи read/write однакові нижчому шару.
// Cal — коефіцієнти; compensatePressure проганяє сирі коди через них.

class Barometer {
public:
    explicit Barometer(Bus bus) : bus_(bus) {}

    bool init() {
        // 1) упізнати чип за фіксованим підписом
        if (bus_.read(REG_CHIP_ID) != EXPECTED_CHIP_ID)
            return false;                          // не той чип / мертва шина

        // 2) один раз вичитати заводські коефіцієнти в пам'ять МК
        readCalibration(bus_, cal_);               // блок з ПЗП -> RAM

        // 3) налаштувати передискретизацію (тиск точніше за температуру) і режим
        bus_.write(REG_OSR, OSR_P_x16 | OSR_T_x2); // важке усереднення на p
        bus_.write(REG_MODE, MODE_NORMAL | ODR_50HZ);
        return true;
    }

    std::optional<float> readPressure() {
        // 4) переконатися, що вимір свіжий
        if (!(bus_.read(REG_STATUS) & STATUS_DATA_READY))
            return std::nullopt;

        // 5) забрати сирі коди: СПОЧАТКУ температура, ПОТІМ тиск (порядок важливий)
        int32_t rawT = read24(bus_, REG_TEMP_RAW);  // 3 байти, 24 біти
        int32_t rawP = read24(bus_, REG_PRESS_RAW);

        // 6) компенсація: сирі коди + коефіцієнти -> справжній тиск, Pa
        return compensatePressure(rawT, rawP, cal_);
    }

private:
    Bus bus_;
    Cal cal_;
};
