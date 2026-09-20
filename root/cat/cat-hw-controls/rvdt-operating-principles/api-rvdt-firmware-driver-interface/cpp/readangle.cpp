RvdtStatus readAngle(uint16_t raw_v1, uint16_t raw_v2, float &angle_deg) noexcept {
    if (!initialized_) {
        return RvdtStatus::ErrParam;
    }
    const float v1 = static_cast<float>(raw_v1);
    const float v2 = static_cast<float>(raw_v2);
    const float sum = v1 + v2;

    if (sum < 10.0f) {
        return RvdtStatus::ErrOpenWinding;
    }

    const float ratiometric = (v1 - v2) / sum;
    const float raw_angle = (ratiometric / config_.sensitivity_v_v_deg) * scale_factor_;
    angle_deg = raw_angle - zero_offset_deg_;

    return RvdtStatus::Ok;
}
