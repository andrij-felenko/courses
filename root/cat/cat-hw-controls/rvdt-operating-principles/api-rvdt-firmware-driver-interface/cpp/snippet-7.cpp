RvdtStatus diagnoseAndRead(uint16_t raw_v1, uint16_t raw_v2, float &angle_deg) noexcept {
    const float v1 = static_cast<float>(raw_v1);
    const float v2 = static_cast<float>(raw_v2);
    const float sum = v1 + v2;

    if (sum < (static_cast<float>(config_.adc_max_raw) * 0.05f)) {
        return RvdtStatus::ErrOpenWinding;
    }

    const auto status = readAngle(raw_v1, raw_v2, angle_deg);
    if (status != RvdtStatus::Ok) {
        return status;
    }

    if (angle_deg > 60.0f || angle_deg < -60.0f) {
        return RvdtStatus::ErrOutOfRange;
    }

    return RvdtStatus::Ok;
}
