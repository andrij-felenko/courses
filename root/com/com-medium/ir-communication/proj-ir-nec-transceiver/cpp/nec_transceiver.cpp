// nec_transceiver.cpp - Реалізація C++ декодера
#include "nec_transceiver.hpp"

namespace ir {

void NecDecoder::handle_edge(uint32_t timestamp_us, bool pin_state) noexcept {
    const uint32_t duration = timestamp_us - last_timestamp_us_;
    last_timestamp_us_ = timestamp_us;

    switch (state_) {
        case State::Idle:
            if (!pin_state) {
                state_ = State::LeaderBurst;
            }
            break;

        case State::LeaderBurst:
            if (pin_state) {
                if (duration >= 7500 && duration <= 10500) {
                    state_ = State::LeaderSpace;
                } else {
                    state_ = State::Idle;
                }
            }
            break;

        case State::LeaderSpace:
            if (!pin_state) {
                if (duration >= 3800 && duration <= 5200) {
                    raw_data_ = 0;
                    bit_index_ = 0;
                    state_ = State::BitPulse;
                } else if (duration >= 1800 && duration <= 2700) {
                    ready_packet_ = NecPacket{.is_repeat = true};
                    state_ = State::Idle;
                } else {
                    state_ = State::Idle;
                }
            }
            break;

        case State::BitPulse:
            if (pin_state) {
                if (duration >= 350 && duration <= 750) {
                    state_ = State::BitSpace;
                } else {
                    state_ = State::Idle;
                }
            }
            break;

        case State::BitSpace:
            if (!pin_state) {
                if (duration >= 400 && duration <= 750) {
                    // Логічний 0
                    ++bit_index_;
                } else if (duration >= 1400 && duration <= 2000) {
                    // Логічна 1
                    raw_data_ |= (1UL << bit_index_);
                    ++bit_index_;
                } else {
                    state_ = State::Idle;
                    break;
                }

                if (bit_index_ >= 32) {
                    NecPacket pkt{
                        .address     = static_cast<uint8_t>(raw_data_ & 0xFF),
                        .address_inv = static_cast<uint8_t>((raw_data_ >> 8) & 0xFF),
                        .command     = static_cast<uint8_t>((raw_data_ >> 16) & 0xFF),
                        .command_inv = static_cast<uint8_t>((raw_data_ >> 24) & 0xFF),
                        .is_repeat   = false
                    };

                    if (pkt.is_valid()) {
                        ready_packet_ = pkt;
                    }
                    state_ = State::Idle;
                } else {
                    state_ = State::BitPulse;
                }
            }
            break;
    }
}

std::optional<NecPacket> NecDecoder::pop_packet() noexcept {
    if (ready_packet_.has_value()) {
        auto pkt = ready_packet_;
        ready_packet_.reset();
        return pkt;
    }
    return std::nullopt;
}

} // namespace ir
