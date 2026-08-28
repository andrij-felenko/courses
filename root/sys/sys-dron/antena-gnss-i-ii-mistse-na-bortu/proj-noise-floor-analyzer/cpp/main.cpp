#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>
#include <string_view>

enum class UbxClass : uint8_t {
    Mon = 0x0A
};

enum class UbxMonId : uint8_t {
    Rf = 0x38
};

enum class AntStatus : uint8_t {
    Init = 0,
    Unknown = 1,
    Ok = 2,
    Short = 3,
    Open = 4
};

enum class JammingState : uint8_t {
    Unknown = 0,
    Clean = 1,
    Warning = 2,
    Critical = 3
};

enum class RfHealthStatus {
    Ok,
    NoiseElevated,
    AgcSaturated,
    CriticalJamming
};

struct RfBlockMetrics {
    uint8_t block_id{0};
    AntStatus ant_status{AntStatus::Unknown};
    uint8_t ant_power{0};
    uint16_t noise_per_ms{0};
    uint16_t agc_cnt{0};
    uint8_t jam_ind{0};
    JammingState jamming_state{JammingState::Unknown};
};

struct RfDiagnosticReport {
    uint8_t version{0};
    uint8_t num_blocks{0};
    std::array<RfBlockMetrics, 4> blocks{};

    [[nodiscard]] constexpr RfHealthStatus evaluate(size_t block_idx, uint16_t baseline_noise) const noexcept {
        if (block_idx >= num_blocks) return RfHealthStatus::Ok;
        const auto& blk = blocks[block_idx];

        if (blk.jam_ind > 100 || blk.jamming_state == JammingState::Critical) {
            return RfHealthStatus::CriticalJamming;
        }
        if (blk.agc_cnt < 4000) {
            return RfHealthStatus::AgcSaturated;
        }
        if (baseline_noise > 0 && blk.noise_per_ms > static_cast<uint16_t>(baseline_noise * 1.3f)) {
            return RfHealthStatus::NoiseElevated;
        }
        return RfHealthStatus::Ok;
    }
};

class UbxMonRfParser {
public:
    enum class ParserError {
        BufferOverflow,
        InvalidChecksum,
        IncompletePayload
    };

    constexpr void reset() noexcept {
        state_ = State::Sync1;
        payload_len_ = 0;
        payload_idx_ = 0;
        ck_a_ = 0;
        ck_b_ = 0;
        calc_ck_a_ = 0;
        calc_ck_b_ = 0;
    }

    [[nodiscard]] std::expected<bool, ParserError> feed_byte(uint8_t b, RfDiagnosticReport& out_report) noexcept {
        switch (state_) {
            case State::Sync1:
                if (b == 0xB5) state_ = State::Sync2;
                break;

            case State::Sync2:
                if (b == 0x62) {
                    state_ = State::Class;
                    calc_ck_a_ = 0;
                    calc_ck_b_ = 0;
                } else {
                    state_ = State::Sync1;
                }
                break;

            case State::Class:
                msg_class_ = b;
                accumulate_ck(b);
                state_ = State::Id;
                break;

            case State::Id:
                msg_id_ = b;
                accumulate_ck(b);
                state_ = State::LenLsb;
                break;

            case State::LenLsb:
                payload_len_ = b;
                accumulate_ck(b);
                state_ = State::LenMsb;
                break;

            case State::LenMsb:
                payload_len_ |= static_cast<uint16_t>(b << 8);
                accumulate_ck(b);
                payload_idx_ = 0;
                if (payload_len_ > max_payload_size) {
                    state_ = State::Sync1;
                    return std::unexpected(ParserError::BufferOverflow);
                }
                state_ = (payload_len_ == 0) ? State::CkA : State::Payload;
                break;

            case State::Payload:
                payload_[payload_idx_++] = b;
                accumulate_ck(b);
                if (payload_idx_ >= payload_len_) {
                    state_ = State::CkA;
                }
                break;

            case State::CkA:
                ck_a_ = b;
                state_ = State::CkB;
                break;

            case State::CkB:
                ck_b_ = b;
                state_ = State::Sync1;
                if (ck_a_ != calc_ck_a_ || ck_b_ != calc_ck_b_) {
                    return std::unexpected(ParserError::InvalidChecksum);
                }
                if (msg_class_ == static_cast<uint8_t>(UbxClass::Mon) &&
                    msg_id_ == static_cast<uint8_t>(UbxMonId::Rf)) {
                    return parse_payload(out_report);
                }
                break;
        }
        return false;
    }

private:
    enum class State {
        Sync1,
        Sync2,
        Class,
        Id,
        LenLsb,
        LenMsb,
        Payload,
        CkA,
        CkB
    };

    static constexpr size_t max_payload_size = 256;

    constexpr void accumulate_ck(uint8_t b) noexcept {
        calc_ck_a_ = static_cast<uint8_t>(calc_ck_a_ + b);
        calc_ck_b_ = static_cast<uint8_t>(calc_ck_b_ + calc_ck_a_);
    }

    [[nodiscard]] std::expected<bool, ParserError> parse_payload(RfDiagnosticReport& out_report) const noexcept {
        if (payload_len_ < 4) {
            return std::unexpected(ParserError::IncompletePayload);
        }
        out_report.version = payload_[0];
        const uint8_t n_blocks = payload_[1];
        out_report.num_blocks = (n_blocks > 4) ? 4 : n_blocks;

        for (uint8_t i = 0; i < out_report.num_blocks; ++i) {
            const size_t offset = 4 + static_cast<size_t>(i) * 24;
            if (offset + 24 > payload_len_) break;

            auto& blk = out_report.blocks[i];
            blk.block_id = payload_[offset + 0];
            blk.ant_status = static_cast<AntStatus>(payload_[offset + 2]);
            blk.ant_power = payload_[offset + 3];
            blk.noise_per_ms = static_cast<uint16_t>(payload_[offset + 8] | (payload_[offset + 9] << 8));
            blk.agc_cnt = static_cast<uint16_t>(payload_[offset + 10] | (payload_[offset + 11] << 8));
            blk.jam_ind = payload_[offset + 12];
            blk.jamming_state = static_cast<JammingState>(payload_[offset + 14]);
        }
        return true;
    }

    State state_{State::Sync1};
    uint8_t msg_class_{0};
    uint8_t msg_id_{0};
    uint16_t payload_len_{0};
    uint16_t payload_idx_{0};
    uint8_t ck_a_{0};
    uint8_t ck_b_{0};
    uint8_t calc_ck_a_{0};
    uint8_t calc_ck_b_{0};
    std::array<uint8_t, max_payload_size> payload_{};
};
