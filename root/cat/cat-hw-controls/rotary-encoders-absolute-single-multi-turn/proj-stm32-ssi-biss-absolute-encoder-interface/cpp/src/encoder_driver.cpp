#include "encoder_driver.hpp"

namespace encoder {

AbsoluteEncoder::AbsoluteEncoder(const EncoderConfig& config) noexcept
    : config_(config), zero_offset_(0) {
    // Обчислюємо маску сумарної позиції на основі розрядності ST + MT
    std::uint8_t total_pos_bits = config_.singleturn_bits + config_.multiturn_bits;
    if (total_pos_bits >= 64) {
        position_mask_ = ~0ULL;
    } else {
        position_mask_ = (1ULL << total_pos_bits) - 1ULL;
    }
}

EncoderStatus AbsoluteEncoder::processFrame(std::uint64_t raw_frame, EncoderData& out_data) noexcept {
    out_data = EncoderData{};

    // 1. Верифікація CRC-6 для протоколу BiSS-C (якщо включено)
    if (config_.protocol == EncoderProtocol::BiSSC) {
        std::uint8_t payload_bits = config_.multiturn_bits + config_.singleturn_bits;
        if (config_.has_error_bit) payload_bits++;
        if (config_.has_warn_bit) payload_bits++;

        std::uint8_t received_crc = static_cast<std::uint8_t>(raw_frame & 0x3FU);
        std::uint64_t payload_data = (raw_frame >> 6) & ((1ULL << payload_bits) - 1ULL);

        std::uint8_t computed_crc = calcCrc6(payload_data, payload_bits);
        if (received_crc != computed_crc) {
            out_data.status = EncoderStatus::CrcError;
            return EncoderStatus::CrcError;
        }

        // Зсуваємо raw_frame вліво від CRC для виділення статусних бітів та позиції
        raw_frame >>= 6;
    }

    // 2. Розбір статусних прапорців nERROR та nWARN (активний рівень 0)
    if (config_.has_warn_bit) {
        out_data.warning_flag = ((raw_frame & 1U) == 0U);
        raw_frame >>= 1;
    }

    if (config_.has_error_bit) {
        out_data.error_flag = ((raw_frame & 1U) == 0U);
        raw_frame >>= 1;
        if (out_data.error_flag) {
            out_data.status = EncoderStatus::HardwareError;
            return EncoderStatus::HardwareError;
        }
    }

    // 3. Виділення бітових полів Singleturn та Multiturn
    std::uint64_t st_mask = (1ULL << config_.singleturn_bits) - 1ULL;
    std::uint64_t raw_st = raw_frame & st_mask;
    raw_frame >>= config_.singleturn_bits;

    std::uint64_t mt_mask = (1ULL << config_.multiturn_bits) - 1ULL;
    std::uint64_t raw_mt = raw_frame & mt_mask;

    // 4. Декодування коду Ґрея (якщо обрано у конфігурації)
    if (config_.encoding == DataEncoding::Gray) {
        raw_st = grayToBinary(raw_st);
        raw_mt = grayToBinary(raw_mt);
    }

    out_data.singleturn_pos = static_cast<std::uint32_t>(raw_st);
    out_data.multiturn_count = static_cast<std::uint32_t>(raw_mt);

    // 5. Розрахунок повної та відносної координати з маскуванням переповнення
    out_data.full_position = (static_cast<std::uint64_t>(raw_mt) << config_.singleturn_bits) | raw_st;

    // Захист від від'ємного переповнення при відніманні віртуального нуля
    out_data.relative_position = (out_data.full_position - zero_offset_) & position_mask_;

    if (out_data.warning_flag) {
        out_data.status = EncoderStatus::WarningLowLight;
    } else {
        out_data.status = EncoderStatus::Ok;
    }

    return out_data.status;
}

void AbsoluteEncoder::setZeroOffset(std::uint64_t current_full_pos) noexcept {
    zero_offset_ = current_full_pos & position_mask_;
}

std::uint64_t AbsoluteEncoder::getZeroOffset() const noexcept {
    return zero_offset_;
}

} // namespace encoder
