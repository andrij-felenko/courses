/**
 * @file Bmp280Driver.tpp
 * @brief Шаблонна реалізація методів драйвера Bmp280Driver C++20.
 */

#pragma once

namespace sf::devices {

template <BusDevice BusImpl>
DriverError Bmp280Driver<BusImpl>::initialize() noexcept {
    // 1. Зчитування Chip ID
    std::array<uint8_t, 1> idBuf{};
    auto err = bus_.read(devAddr_, 0xD0, std::span<uint8_t>(idBuf));
    if (err != DriverError::None) {
        ++errorCount_;
        return err;
    }

    if (idBuf[0] != ChipIdExpected) {
        ++errorCount_;
        return DriverError::InvalidChipId;
    }

    // 2. Soft reset
    const std::array<uint8_t, 1> resetCmd{0xB6};
    err = bus_.write(devAddr_, 0xE0, std::span<const uint8_t>(resetCmd));
    if (err != DriverError::None) {
        ++errorCount_;
        return err;
    }

    bus_.delayMs(10);

    // 3. Зчитування таблиці калібрувальних коефіцієнтів
    err = readCalibrationTable();
    if (err != DriverError::None) {
        ++errorCount_;
        return err;
    }

    return DriverError::None;
}

template <BusDevice BusImpl>
DriverError Bmp280Driver<BusImpl>::readCalibrationTable() noexcept {
    std::array<uint8_t, 24> rawCalib{};
    auto err = bus_.read(devAddr_, 0x88, std::span<uint8_t>(rawCalib));
    if (err != DriverError::None) {
        return err;
    }

    calib_.dig_T1 = static_cast<uint16_t>(rawCalib[0] | (static_cast<uint16_t>(rawCalib[1]) << 8));
    calib_.dig_T2 = static_cast<int16_t>(rawCalib[2] | (static_cast<uint16_t>(rawCalib[3]) << 8));
    calib_.dig_T3 = static_cast<int16_t>(rawCalib[4] | (static_cast<uint16_t>(rawCalib[5]) << 8));

    calib_.dig_P1 = static_cast<uint16_t>(rawCalib[6] | (static_cast<uint16_t>(rawCalib[7]) << 8));
    calib_.dig_P2 = static_cast<int16_t>(rawCalib[8] | (static_cast<uint16_t>(rawCalib[9]) << 8));
    calib_.dig_P3 = static_cast<int16_t>(rawCalib[10] | (static_cast<uint16_t>(rawCalib[11]) << 8));
    calib_.dig_P4 = static_cast<int16_t>(rawCalib[12] | (static_cast<uint16_t>(rawCalib[13]) << 8));
    calib_.dig_P5 = static_cast<int16_t>(rawCalib[14] | (static_cast<uint16_t>(rawCalib[15]) << 8));
    calib_.dig_P6 = static_cast<int16_t>(rawCalib[16] | (static_cast<uint16_t>(rawCalib[17]) << 8));
    calib_.dig_P7 = static_cast<int16_t>(rawCalib[18] | (static_cast<uint16_t>(rawCalib[19]) << 8));
    calib_.dig_P8 = static_cast<int16_t>(rawCalib[20] | (static_cast<uint16_t>(rawCalib[21]) << 8));
    calib_.dig_P9 = static_cast<int16_t>(rawCalib[22] | (static_cast<uint16_t>(rawCalib[23]) << 8));

    if (calib_.dig_T1 == 0 || calib_.dig_T1 == 0xFFFF || calib_.dig_P1 == 0 || calib_.dig_P1 == 0xFFFF) {
        return DriverError::CalibrationCorrupted;
    }

    return DriverError::None;
}

template <BusDevice BusImpl>
DriverError Bmp280Driver<BusImpl>::configure(OverSampling osrT, OverSampling osrP, SensorMode mode, IirFilter filter) noexcept {
    const std::array<uint8_t, 1> configReg{static_cast<uint8_t>(static_cast<uint8_t>(filter) << 2)};
    auto err = bus_.write(devAddr_, 0xF5, std::span<const uint8_t>(configReg));
    if (err != DriverError::None) {
        ++errorCount_;
        return err;
    }

    const std::array<uint8_t, 1> ctrlMeas{static_cast<uint8_t>(
        (static_cast<uint8_t>(osrT) << 5) |
        (static_cast<uint8_t>(osrP) << 2) |
        static_cast<uint8_t>(mode)
    )};

    err = bus_.write(devAddr_, 0xF4, std::span<const uint8_t>(ctrlMeas));
    if (err != DriverError::None) {
        ++errorCount_;
        return err;
    }

    return DriverError::None;
}

template <BusDevice BusImpl>
SensorSample Bmp280Driver<BusImpl>::compensate(std::span<const uint8_t, BurstReadSize> raw) noexcept {
    const int32_t adcP = static_cast<int32_t>((static_cast<uint32_t>(raw[0]) << 12) |
                                              (static_cast<uint32_t>(raw[1]) << 4)  |
                                              (static_cast<uint32_t>(raw[2]) >> 4));

    const int32_t adcT = static_cast<int32_t>((static_cast<uint32_t>(raw[3]) << 12) |
                                              (static_cast<uint32_t>(raw[4]) << 4)  |
                                              (static_cast<uint32_t>(raw[5]) >> 4));

    // Температурна компенсація
    const int32_t var1T = ((((adcT >> 3) - (static_cast<int32_t>(calib_.dig_T1) << 1))) * static_cast<int32_t>(calib_.dig_T2)) >> 11;
    const int32_t var2T = (((((adcT >> 4) - static_cast<int32_t>(calib_.dig_T1)) *
                             ((adcT >> 4) - static_cast<int32_t>(calib_.dig_T1))) >> 12) *
                           static_cast<int32_t>(calib_.dig_T3)) >> 14;

    tFine_ = var1T + var2T;
    const float tempDegC = static_cast<float>((tFine_ * 5 + 128) >> 8) / 100.0f;

    // Компенсація тиску
    int64_t var1P = static_cast<int64_t>(tFine_) - 128000;
    int64_t var2P = var1P * var1P * static_cast<int64_t>(calib_.dig_P6);
    var2P = var2P + ((var1P * static_cast<int64_t>(calib_.dig_P5)) << 17);
    var2P = var2P + (static_cast<int64_t>(calib_.dig_P4) << 35);
    var1P = ((var1P * var1P * static_cast<int64_t>(calib_.dig_P3)) >> 8) +
            ((var1P * static_cast<int64_t>(calib_.dig_P2)) << 12);
    var1P = (((static_cast<int64_t>(1) << 47) + var1P)) * static_cast<int64_t>(calib_.dig_P1) >> 33;

    if (var1P == 0) {
        return SensorSample{.temperature = units::Celsius(tempDegC), .pressure = units::Pascals(0.0f), .isValid = false};
    }

    int64_t p = 1048576 - adcP;
    p = (((p << 31) - var2P) * 3125) / var1P;
    var1P = (static_cast<int64_t>(calib_.dig_P9) * (p >> 13) * (p >> 13)) >> 25;
    var2P = (static_cast<int64_t>(calib_.dig_P8) * p) >> 19;
    p = ((p + var1P + var2P) >> 8) + (static_cast<int64_t>(calib_.dig_P7) << 4);

    const float pressPa = static_cast<float>(p) / 256.0f;

    return SensorSample{
        .temperature = units::Celsius(tempDegC),
        .pressure = units::Pascals(pressPa),
        .timestampUs = 0,
        .isValid = true
    };
}

template <BusDevice BusImpl>
std::optional<SensorSample> Bmp280Driver<BusImpl>::readSynchronous() noexcept {
    std::array<uint8_t, BurstReadSize> rawData{};
    auto err = bus_.read(devAddr_, 0xF7, std::span<uint8_t>(rawData));
    if (err != DriverError::None) {
        ++errorCount_;
        return std::nullopt;
    }

    lastSample_ = compensate(std::span<const uint8_t, BurstReadSize>(rawData));
    return lastSample_;
}

template <BusDevice BusImpl>
DriverError Bmp280Driver<BusImpl>::startDmaRead() noexcept {
    if (isBusyDma_) {
        return DriverError::Busy;
    }
    isBusyDma_ = true;
    auto err = bus_.readDmaAsync(devAddr_, 0xF7, std::span<uint8_t>(dmaBuffer_));
    if (err != DriverError::None) {
        isBusyDma_ = false;
        ++errorCount_;
    }
    return err;
}

template <BusDevice BusImpl>
void Bmp280Driver<BusImpl>::onDmaComplete() noexcept {
    isBusyDma_ = false;
    lastSample_ = compensate(std::span<const uint8_t, BurstReadSize>(dmaBuffer_));
}

template <BusDevice BusImpl>
DriverError Bmp280Driver<BusImpl>::recover() noexcept {
    bus_.resetBus();
    bus_.delayMs(15);
    return initialize();
}

} // namespace sf::devices
