namespace embedded::naive {

void SetRelayPower(bool enable) noexcept;

void TemperatureControlStep(float current_temperature) noexcept {
    constexpr float Threshold = 25.0f;

    if (current_temperature < Threshold) {
        SetRelayPower(true);   // Увімкнути нагрів
    } else {
        SetRelayPower(false);  // Вимкнути нагрів
    }
}

} // namespace embedded::naive
