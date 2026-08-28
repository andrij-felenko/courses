struct SensorData {
    uint16_t raw_adc;
};

std::optional<SensorData> read_sensor() noexcept;
std::optional<float> convert_to_voltage(SensorData s) noexcept;
std::optional<float> calibrate(float v) noexcept;

std::optional<float> get_calibrated_voltage() noexcept {
    return read_sensor()
        .and_then(convert_to_voltage)
        .and_then(calibrate);
}
