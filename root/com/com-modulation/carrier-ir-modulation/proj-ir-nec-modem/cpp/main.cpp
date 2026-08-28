// cpp — C++17 об'єктна інкапсуляція декодера з std::optional та noexcept
#include <cstdint>
#include <optional>

struct NecCommand {
    uint8_t  address{0};
    uint8_t  command{0};
    uint32_t raw_code{0};
    bool     is_repeat{false};
};

class NecDecoder {
public:
    enum class State : uint8_t {
        Idle,
        HeaderSpace,
        BitPulse,
        BitSpace
    };

    void process_edge(uint32_t delta_us, bool pin_state_low) noexcept {
        switch (state_) {
            case State::Idle:
                if (pin_state_low && is_in_range(delta_us, 8000, 10000)) {
                    state_ = State::HeaderSpace;
                }
                break;

            case State::HeaderSpace:
                if (!pin_state_low) {
                    if (is_in_range(delta_us, 4000, 5000)) {
                        shift_reg_ = 0;
                        bit_count_ = 0;
                        state_ = State::BitPulse;
                    } else if (is_in_range(delta_us, 2000, 2600) && last_valid_command_) {
                        last_valid_command_->is_repeat = true;
                        pending_command_ = last_valid_command_;
                        state_ = State::Idle;
                    } else {
                        state_ = State::Idle;
                    }
                }
                break;

            case State::BitPulse:
                if (pin_state_low && is_in_range(delta_us, 400, 750)) {
                    state_ = State::BitSpace;
                } else {
                    state_ = State::Idle;
                }
                break;

            case State::BitSpace:
                if (!pin_state_low) {
                    shift_reg_ >>= 1;
                    if (is_in_range(delta_us, 1400, 1950)) {
                        shift_reg_ |= 0x80000000U; // Логічна '1'
                    } else if (!is_in_range(delta_us, 400, 850)) {
                        state_ = State::Idle;     // Збій таймингу
                        break;
                    }

                    if (++bit_count_ >= 32) {
                        auto parsed = parse_frame(shift_reg_);
                        if (parsed) {
                            last_valid_command_ = parsed;
                            pending_command_    = parsed;
                        }
                        state_ = State::Idle;
                    } else {
                        state_ = State::BitPulse;
                    }
                }
                break;
        }
    }

    [[nodiscard]] std::optional<NecCommand> poll_command() noexcept {
        auto cmd = pending_command_;
        pending_command_.reset();
        return cmd;
    }

private:
    State state_{State::Idle};
    uint32_t shift_reg_{0};
    uint8_t  bit_count_{0};
    std::optional<NecCommand> pending_command_{std::nullopt};
    std::optional<NecCommand> last_valid_command_{std::nullopt};

    static constexpr bool is_in_range(uint32_t val, uint32_t min_v, uint32_t max_v) noexcept {
        return val >= min_v && val <= max_v;
    }

    static std::optional<NecCommand> parse_frame(uint32_t raw) noexcept {
        const uint8_t addr  = (raw >> 0)  & 0xFF;
        const uint8_t naddr = (raw >> 8)  & 0xFF;
        const uint8_t cmd   = (raw >> 16) & 0xFF;
        const uint8_t ncmd  = (raw >> 24) & 0xFF;

        if ((addr ^ naddr) == 0xFF && (cmd ^ ncmd) == 0xFF) {
            return NecCommand{addr, cmd, raw, false};
        }
        return std::nullopt;
    }
};
