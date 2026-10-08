// Реалізація методів калібрування та обробки у C++
LvdtDriver::Status calibrateZero(LvdtDriver::Calibration& calib, float last_raw_ratio) {
    calib.zero_offset_ratio = last_raw_ratio;
    return LvdtDriver::Status::Ok;
}

LvdtDriver::Status processPosition(const LvdtDriver::Config& config, 
                                    const LvdtDriver::Calibration& calib,
                                    float u_s1_amp, float u_s2_amp, 
                                    float& last_raw_ratio, float& position_mm) {
    float u_sum = u_s1_amp + u_s2_amp;
    if (u_sum < config.min_sum_threshold) {
        return LvdtDriver::Status::ExcitationLost;
    }

    float u_diff = u_s1_amp - u_s2_amp;
    float v_ratio = u_diff / u_sum;
    last_raw_ratio = v_ratio;

    float x_raw = (v_ratio - calib.zero_offset_ratio) * calib.scale_factor_mm;

    float x_lin = calib.poly_c0 +
                  calib.poly_c1 * x_raw +
                  calib.poly_c2 * (x_raw * x_raw) +
                  calib.poly_c3 * (x_raw * x_raw * x_raw);

    position_mm = x_lin;
    return LvdtDriver::Status::Ok;
}
