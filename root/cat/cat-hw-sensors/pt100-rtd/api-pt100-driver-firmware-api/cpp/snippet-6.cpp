Pt100Driver::Status Pt100Driver::readTemperatureC(float& out_temp_c) {
    if (!is_initialized_) {
        return Status::HardwareFault;
    }

    uint32_t raw_adc = 0;
    if (!readAdcRaw(raw_adc)) {
        out_temp_c = -999.0f;
        return Status::CommunicationError;
    }

    if (raw_adc >= 0xFFFFFE) {
        out_temp_c = -999.0f;
        return Status::HardwareFault; // Обрив лінії
    }

    float r_rtd = config_.r_ref_ohms * (static_cast<float>(raw_adc) / 8388607.0f);
    out_temp_c = calculateCvdTemperature(r_rtd, config_.r_0_ohms);
    return Status::Ok;
}
