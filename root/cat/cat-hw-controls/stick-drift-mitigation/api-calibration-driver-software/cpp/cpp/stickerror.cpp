enum class StickError {
    Ok = 0,
    NullPointer = -1,
    InvalidCalibration = -2
};

struct StickConfig {
    uint16_t raw_x_zero = 2048;
    uint16_t raw_y_zero = 2048;
    float deadzone_radial = 0.05f;
};

class StickDriver {
public:
    StickError calibrateNeutral(const uint16_t* x_samples, const uint16_t* y_samples, size_t count) {
        if (!x_samples || !y_samples || count == 0) return StickError::NullPointer;
        uint32_t sum_x = 0, sum_y = 0;
        for (size_t i = 0; i < count; ++i) {
            sum_x += x_samples[i];
            sum_y += y_samples[i];
        }
        config_.raw_x_zero = static_cast<uint16_t>(sum_x / count);
        config_.raw_y_zero = static_cast<uint16_t>(sum_y / count);
        return StickError::Ok;
    }
private:
    StickConfig config_;
};
