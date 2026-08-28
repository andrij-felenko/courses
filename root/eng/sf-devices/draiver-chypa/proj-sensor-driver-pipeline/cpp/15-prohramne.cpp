class AltitudeComplementaryFilter {
public:
    constexpr AltitudeComplementaryFilter(float kp, float ki) noexcept : kp_(kp), ki_(ki) {}

    void update(units::Pascals press, float accelZ, float dt) noexcept {
        const float baroAlt = 44330.0f * (1.0f - std::pow(press.value() / 101325.0f, 1.0f / 5.255f));
        const float accelCorrected = accelZ - accelBias_;
        altitude_ += velocity_ * dt + 0.5f * accelCorrected * dt * dt;
        velocity_ += accelCorrected * dt;

        const float error = baroAlt - altitude_;
        altitude_ += error * kp_ * dt;
        velocity_ += error * ki_ * dt;
        accelBias_ -= error * (ki_ * 0.1f) * dt;
    }

    [[nodiscard]] float altitudeMeters() const noexcept { return altitude_; }
    [[nodiscard]] float velocityMps() const noexcept { return velocity_; }
private:
    float altitude_{0.0f};
    float velocity_{0.0f};
    float accelBias_{0.0f};
    float kp_{1.5f};
    float ki_{0.8f};
};
