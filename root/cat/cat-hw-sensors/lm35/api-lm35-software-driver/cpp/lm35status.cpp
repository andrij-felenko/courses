enum class LM35Status {
    Ok = 0,
    InvalidParam,
    Underflow,
    Overflow,
    InvalidRawCode
};

// Метод класу LM35Driver
LM35Status readTemperature(uint32_t raw_adc, float& out_temp) const {
    if (raw_adc > max_adc_raw_) {
        return LM35Status::InvalidRawCode;
    }
    float temp = readCelsius(raw_adc);
    if (temp < -5.0f) {
        return LM35Status::Underflow;
    }
    if (temp > 105.0f) {
        return LM35Status::Overflow;
    }
    out_temp = temp;
    return LM35Status::Ok;
}
