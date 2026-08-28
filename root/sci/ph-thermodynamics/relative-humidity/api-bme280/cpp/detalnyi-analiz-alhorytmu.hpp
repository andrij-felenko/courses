// C++17 constexpr компенсація вологості (повертає відсотки %RH)
[[nodiscard]] constexpr double compensate_humidity_cpp(int32_t adc_H, int32_t t_fine, const CalibrationData& calib) noexcept {
    int32_t v_x1 = (t_fine - 76800);
    v_x1 = (((((adc_H << 14) - (static_cast<int32_t>(calib.dig_H4) << 20) - (static_cast<int32_t>(calib.dig_H5) * v_x1)) + 16384) >> 15) *
            (((((((v_x1 * static_cast<int32_t>(calib.dig_H6)) >> 10) * (((v_x1 * static_cast<int32_t>(calib.dig_H3)) >> 11) + 32768)) >> 10) + 2097152) *
              static_cast<int32_t>(calib.dig_H2) + 8192) >> 14));
    v_x1 = (v_x1 - (((((v_x1 >> 15) * (v_x1 >> 15)) >> 7) * static_cast<int32_t>(calib.dig_H1)) >> 4));
    v_x1 = std::clamp(v_x1, 0, 419430400);
    return static_cast<double>(v_x1 >> 12) / 1024.0;
}
