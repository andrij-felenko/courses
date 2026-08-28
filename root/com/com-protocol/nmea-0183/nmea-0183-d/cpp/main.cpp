#include <cstdint>
#include <string_view>
#include <optional>
#include <array>

class NmeaFsm {
public:
    enum class State {
        WaitStart,
        ReadPayload,
        ReadCs1,
        ReadCs2,
        WaitCr,
        WaitLf
    };

    std::optional<std::string_view> feed(uint8_t byte) noexcept {
        if (byte == '$' || byte == '!') {
            state_ = State::ReadPayload;
            idx_ = 0;
            calc_crc_ = 0;
            return std::nullopt;
        }

        switch (state_) {
            case State::WaitStart:
                return std::nullopt;

            case State::ReadPayload:
                if (byte == '*') {
                    buffer_[idx_] = '\0';
                    state_ = State::ReadCs1;
                } else if (idx_ < buffer_.size() - 4) {
                    buffer_[idx_++] = static_cast<char>(byte);
                    calc_crc_ ^= byte;
                } else {
                    state_ = State::WaitStart;
                }
                return std::nullopt;

            case State::ReadCs1: {
                int v = hexVal(static_cast<char>(byte));
                if (v >= 0) {
                    rx_crc_ = static_cast<uint8_t>(v << 4);
                    state_ = State::ReadCs2;
                } else {
                    state_ = State::WaitStart;
                }
                return std::nullopt;
            }

            case State::ReadCs2: {
                int v = hexVal(static_cast<char>(byte));
                if (v >= 0) {
                    rx_crc_ |= static_cast<uint8_t>(v);
                    state_ = (rx_crc_ == calc_crc_) ? State::WaitCr : State::WaitStart;
                } else {
                    state_ = State::WaitStart;
                }
                return std::nullopt;
            }

            case State::WaitCr:
                state_ = (byte == '\r') ? State::WaitLf : State::WaitStart;
                return std::nullopt;

            case State::WaitLf:
                state_ = State::WaitStart;
                if (byte == '\n') {
                    return std::string_view(buffer_.data(), idx_);
                }
                return std::nullopt;
        }
        return std::nullopt;
    }

private:
    static constexpr int hexVal(char c) noexcept {
        if (c >= '0' && c <= '9') return c - '0';
        if (c >= 'A' && c <= 'F') return c - 'A' + 10;
        return -1;
    }

    State state_{State::WaitStart};
    std::array<char, 84> buffer_{};
    size_t idx_{0};
    uint8_t calc_crc_{0};
    uint8_t rx_crc_{0};
};
