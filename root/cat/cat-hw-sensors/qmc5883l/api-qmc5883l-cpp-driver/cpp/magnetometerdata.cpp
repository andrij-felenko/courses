struct MagnetometerData {
    int16_t x;
    int16_t y;
    int16_t z;
    bool overflow;
};

DriverStatus readRawData(MagnetometerData& outData) {
    uint8_t status = 0;
    if (!m_bus.readRegisters(I2C_ADDR, 0x06, &status, 1)) {
        return DriverStatus::ErrI2C;
    }

    // Перевірка прапорця готовності даних DRDY (біт 0)
    if ((status & 0x01) == 0) {
        return DriverStatus::ErrDataNotReady;
    }

    // Зчитування 6 байтів вимірювань (0x00..0x05)
    uint8_t rawBuf[6];
    if (!m_bus.readRegisters(I2C_ADDR, 0x00, rawBuf, 6)) {
        return DriverStatus::ErrI2C;
    }

    outData.x = static_cast<int16_t>((rawBuf[1] << 8) | rawBuf[0]);
    outData.y = static_cast<int16_t>((rawBuf[3] << 8) | rawBuf[2]);
    outData.z = static_cast<int16_t>((rawBuf[5] << 8) | rawBuf[4]);
    outData.overflow = (status & 0x02) != 0; // Перевірка прапорця OVL (біт 1)

    return DriverStatus::Ok;
}
