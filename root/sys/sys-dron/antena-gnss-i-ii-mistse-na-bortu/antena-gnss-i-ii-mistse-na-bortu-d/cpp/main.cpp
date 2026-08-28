#include <cstdint>
#include <cstddef>
#include <array>
#include <optional>
#include <span>

struct RfMetrics {
    uint8_t block_id{0};
    uint16_t noise_per_ms{0};
    uint16_t agc_cnt{0};
    uint8_t jam_ind{0};
    uint8_t jamming_state{0};

    [[nodiscard]] constexpr bool is_healthy(uint16_t max_allowed_noise) const noexcept {
        return (jam_ind < 80) && (jamming_state <= 1) && (noise_per_ms <= max_allowed_noise) && (agc_cnt > 4000);
    }
};

class UbxStreamDecoder {
public:
    constexpr void reset() noexcept {
        step_ = Step::Sync1;
        calc_a_ = 0;
        calc_b_ = 0;
        index_ = 0;
    }

    [[nodiscard]] std::optional<RfMetrics> process_byte(uint8_t byte) noexcept {
        switch (step_) {
            case Step::Sync1:
                if (byte == 0xB5) step_ = Step::Sync2;
                break;

            case Step::Sync2:
                if (byte == 0x62) {
                    step_ = Step::Class;
                    calc_a_ = 0;
                    calc_b_ = 0;
                } else {
                    step_ = Step::Sync1;
                }
                break;

            case Step::Class:
                msg_class_ = byte;
                accumulate(byte);
                step_ = Step::Id;
                break;

            case Step::Id:
                msg_id_ = byte;
                accumulate(byte);
                step_ = Step::LenLsb;
                break;

            case Step::LenLsb:
                length_ = byte;
                accumulate(byte);
                step_ = Step::LenMsb;
                break;

            case Step::LenMsb:
                length_ |= static_cast<uint16_t>(byte << 8);
                accumulate(byte);
                index_ = 0;
                if (length_ > buffer_.size() || length_ < 4) {
                    step_ = Step::Sync1;
                } else {
                    step_ = Step::Payload;
                }
                break;

            case Step::Payload:
                buffer_[index_++] = byte;
                accumulate(byte);
                if (index_ >= length_) step_ = Step::CkA;
                break;

            case Step::CkA:
                ck_a_ = byte;
                step_ = Step::CkB;
                break;

            case Step::CkB:
                ck_b_ = byte;
                step_ = Step::Sync1;
                if (ck_a_ == calc_a_ && ck_b_ == calc_b_) {
                    if (msg_class_ == 0x0A && msg_id_ == 0x38) {
                        const uint8_t n_blocks = buffer_[1];
                        if (n_blocks > 0 && length_ >= 28) {
                            RfMetrics m{};
                            m.block_id = buffer_[4];
                            m.noise_per_ms = static_cast<uint16_t>(buffer_[12] | (buffer_[13] << 8));
                            m.agc_cnt = static_cast<uint16_t>(buffer_[14] | (buffer_[15] << 8));
                            m.jam_ind = buffer_[16];
                            m.jamming_state = buffer_[18];
                            return m;
                        }
                    }
                }
                break;
        }
        return std::nullopt;
    }

private:
    enum class Step {
        Sync1, Sync2, Class, Id, LenLsb, LenMsb, Payload, CkA, CkB
    };

    constexpr void accumulate(uint8_t b) noexcept {
        calc_a_ = static_cast<uint8_t>(calc_a_ + b);
        calc_b_ = static_cast<uint8_t>(calc_b_ + calc_a_);
    }

    Step step_{Step::Sync1};
    uint8_t msg_class_{0};
    uint8_t msg_id_{0};
    uint16_t length_{0};
    uint16_t index_{0};
    uint8_t ck_a_{0};
    uint8_t ck_b_{0};
    uint8_t calc_a_{0};
    uint8_t calc_b_{0};
    std::array<uint8_t, 128> buffer_{};
};
