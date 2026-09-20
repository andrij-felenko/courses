#include "SsiEncoder.hpp"

namespace hw_controls {

SsiEncoder::SsiEncoder(const SsiConfig& config) : config_(config) {}

uint32_t SsiEncoder::grayToBinary(uint32_t gray) noexcept {
    uint32_t mask = gray >> 1;
    while (mask != 0) {
        gray ^= mask;
        mask >>= 1;
    }
    return gray;
}

bool SsiEncoder::checkParity(uint32_t val) noexcept {
    uint32_t count = 0;
    while (val) {
        count += (val & 1);
        val >>= 1;
    }
    return (count % 2) == 0;
}

std::optional<EncoderPosition> SsiEncoder::decodeFrame(uint32_t frame_word, bool hardware_error_pin) const {
    EncoderPosition pos;
    pos.status = EncoderStatus::Ok;

    if (hardware_error_pin) {
        pos.status = pos.status | EncoderStatus::HardwareError;
        return std::nullopt;
    }

    if (config_.check_parity) {
        bool parity_bit = (frame_word & 0x01) != 0;
        uint32_t data_payload = frame_word >> 1;
        if (checkParity(data_payload) != parity_bit) {
            pos.status = pos.status | EncoderStatus::ParityError;
            return std::nullopt;
        }
        frame_word >>= 1;
    }

    bool n_err = (frame_word & 0x01) != 0;
    frame_word >>= 1;
    if (!n_err) {
        pos.status = pos.status | EncoderStatus::HardwareError;
        return std::nullopt;
    }

    uint32_t st_mask = (1U << config_.singleturn_bits) - 1;
    uint32_t mt_mask = (1U << config_.multiturn_bits) - 1;

    uint32_t raw_st = frame_word & st_mask;
    uint32_t raw_mt = (frame_word >> config_.singleturn_bits) & mt_mask;

    pos.singleturn_raw = config_.use_gray_code ? grayToBinary(raw_st) : raw_st;
    pos.multiturn_raw  = config_.use_gray_code ? grayToBinary(raw_mt) : raw_mt;

    float max_counts = static_cast<float>(1U << config_.singleturn_bits);
    pos.angle_deg = (static_cast<float>(pos.singleturn_raw) / max_counts) * 360.0f;
    pos.turns = static_cast<int32_t>(pos.multiturn_raw);

    return pos;
}

} // namespace hw_controls
