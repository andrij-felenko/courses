#pragma once

#include <cstdint>
#include <array>
#include <optional>

namespace hw_controls {

enum class EncoderStatus : uint8_t {
    Ok = 0,
    ParityError = (1 << 0),
    HardwareError = (1 << 1),
    TimeoutError = (1 << 2)
};

inline EncoderStatus operator|(EncoderStatus a, EncoderStatus b) {
    return static_cast<EncoderStatus>(static_cast<uint8_t>(a) | static_cast<uint8_t>(b));
}

inline bool operator&(EncoderStatus a, EncoderStatus b) {
    return (static_cast<uint8_t>(a) & static_cast<uint8_t>(b)) != 0;
}

struct SsiConfig {
    uint8_t singleturn_bits{13}; // 13-bit ST (8192)
    uint8_t multiturn_bits{12};  // 12-bit MT (4096)
    bool use_gray_code{true};
    bool check_parity{true};
};

struct EncoderPosition {
    uint32_t singleturn_raw{0};
    uint32_t multiturn_raw{0};
    float angle_deg{0.0f};
    int32_t turns{0};
    EncoderStatus status{EncoderStatus::Ok};
};

class SsiEncoder {
public:
    explicit SsiEncoder(const SsiConfig& config = {});

    [[nodiscard]] std::optional<EncoderPosition> decodeFrame(uint32_t frame_word, bool hardware_error_pin = false) const;

    [[nodiscard]] static uint32_t grayToBinary(uint32_t gray) noexcept;
    [[nodiscard]] static bool checkParity(uint32_t val) noexcept;

private:
    SsiConfig config_;
};

} // namespace hw_controls
