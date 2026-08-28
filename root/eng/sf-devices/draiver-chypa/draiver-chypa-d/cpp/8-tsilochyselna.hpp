std::optional<SensorSample> Bmp280Driver<BusImpl>::compensate(std::span<const uint8_t, 6> raw) noexcept {
    const int32_t adcP = (static_cast<uint32_t>(raw[0]) << 12) |
                         (static_cast<uint32_t>(raw[1]) << 4)  |
                         (static_cast<uint32_t>(raw[2]) >> 4);

    const int32_t adcT = (static_cast<uint32_t>(raw[3]) << 12) |
                         (static_cast<uint32_t>(raw[4]) << 4)  |
                         (static_cast<uint32_t>(raw[5]) >> 4);

    const int32_t var1T = ((((adcT >> 3) - (static_cast<int32_t>(calib_.dig_T1) << 1))) * static_cast<int32_t>(calib_.dig_T2)) >> 11;
    const int32_t var2T = (((((adcT >> 4) - static_cast<int32_t>(calib_.dig_T1)) *
                             ((adcT >> 4) - static_cast<int32_t>(calib_.dig_T1))) >> 12) *
                           static_cast<int32_t>(calib_.dig_T3)) >> 14;

    tFine_ = var1T + var2T;
    const float tempC = static_cast<float>((tFine_ * 5 + 128) >> 8) / 100.0f;

    int64_t var1P = static_cast<int64_t>(tFine_) - 128000;
    int64_t var2P = var1P * var1P * static_cast<int64_t>(calib_.dig_P6);
    var2P = var2P + ((var1P * static_cast<int64_t>(calib_.dig_P5)) << 17);
    var2P = var2P + (static_cast<int64_t>(calib_.dig_P4) << 35);
    var1P = ((var1P * var1P * static_cast<int64_t>(calib_.dig_P3)) >> 8) +
            ((var1P * static_cast<int64_t>(calib_.dig_P2)) << 12);
    var1P = (((static_cast<int64_t>(1) << 47) + var1P)) * static_cast<int64_t>(calib_.dig_P1) >> 33;

    if (var1P == 0) return std::nullopt;

    int64_t p = 1048576 - adcP;
    p = (((p << 31) - var2P) * 3125) / var1P;
    var1P = (static_cast<int64_t>(calib_.dig_P9) * (p >> 13) * (p >> 13)) >> 25;
    var2P = (static_cast<int64_t>(calib_.dig_P8) * p) >> 19;
    p = ((p + var1P + var2P) >> 8) + (static_cast<int64_t>(calib_.dig_P7) << 4);

    return SensorSample{
        .temperature = units::Celsius(tempC),
        .pressure = units::Pascals(static_cast<float>(p) / 256.0f),
        .timestampUs = 0,
        .isValid = true
    };
}
