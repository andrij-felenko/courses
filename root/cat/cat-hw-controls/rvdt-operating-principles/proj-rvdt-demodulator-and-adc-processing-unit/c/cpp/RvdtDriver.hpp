#pragma once

#include <cstdint>
#include <cmath>
#include <optional>

namespace hw_controls {

enum class RvdtError : uint8_t {
    Ok = 0,
    OpenCircuit = (1 << 0),
    ShortCircuit = (1 << 1),
    OutOfRange = (1 << 2)
};

inline RvdtError operator|(RvdtError a, RvdtError b) noexcept {
    return static_cast<RvdtError>(static_cast<uint8_t>(a) | static_cast<uint8_t>(b));
}

inline bool operator&(RvdtError a, RvdtError b) noexcept {
    return (static_cast<uint8_t>(a) & static_cast<uint8_t>(b)) != 0;
}

struct RvdtConfig {
    float max_angle_deg{45.0f};
    float sensitivity_v_v_deg{0.025f};
    float zero_offset_deg{0.0f};
    float min_sum_voltage_v{0.5f};
    float max_sum_voltage_v{15.0f};
    float alpha_filter{0.25f};
};

struct RvdtReading {
    float raw_angle_deg{0.0f};
    float filtered_angle_deg{0.0f};
    float v_s1{0.0f};
    float v_s2{0.0f};
    float sum_voltage{0.0f};
    float diff_voltage{0.0f};
    RvdtError error{RvdtError::Ok};
};

class RvdtDriver {
public:
    explicit RvdtDriver(const RvdtConfig& config = {}) noexcept;

    [[nodiscard]] RvdtReading processSample(float v_s1, float v_s2) noexcept;
    void calibrateZero() noexcept;

    [[nodiscard]] const RvdtConfig& config() const noexcept { return config_; }
    void setConfig(const RvdtConfig& config) noexcept { config_ = config; }

private:
    RvdtConfig config_;
    RvdtReading last_reading_;
};

} // namespace hw_controls
