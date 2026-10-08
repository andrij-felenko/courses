#include <cstdint>
#include <cmath>

enum class RtdCalcMode {
    Cvd = 0,
    Lut = 1
};

enum class RtdStatus : uint8_t {
    Ok               = 0x00,
    OpenCircuit      = 0x01,
    ShortCircuit     = 0x02,
    OutOfRange       = 0x04,
    InvalidArg       = 0x08
};

struct RtdConfig {
    float r0{100.0f};
    float alpha{0.003851f};
    float cvd_a{3.9083e-3f};
    float cvd_b{-5.775e-7f};
    float cvd_c{-4.183e-12f};
    float r_ref{400.0f};
    float r_min{10.0f};
    float r_max{400.0f};
    RtdCalcMode mode{RtdCalcMode::Cvd};
};

class RtdPipeline {
public:
    RtdPipeline() = default;

    RtdStatus init(const RtdConfig& cfg) {
        if (cfg.r0 <= 0.0f || cfg.r_ref <= 0.0f || cfg.r_min >= cfg.r_max) {
            return RtdStatus::InvalidArg;
        }
        config_ = cfg;
        zero_offset_ = 0.0f;
        span_gain_ = 1.0f;
        initialized_ = true;
        return RtdStatus::Ok;
    }

    bool isInitialized() const { return initialized_; }
    const RtdConfig& config() const { return config_; }

private:
    RtdConfig config_{};
    float zero_offset_{0.0f};
    float span_gain_{1.0f};
    bool initialized_{false};
};
