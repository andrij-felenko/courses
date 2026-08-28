// nec_driver.hpp - Ідіоматична реалізація декодера NEC мовою C++
#pragma once

#include <cstdint>
#include <optional>

namespace optical {

struct NecMessage {
    uint8_t address{0};
    uint8_t command{0};
    bool is_repeat{false};
};

class NecReceiver {
public:
    enum class State : uint8_t {
        Idle,
        LeaderBurst,
        LeaderSpace,
        DataBit
    };

    constexpr NecReceiver() noexcept = default;

    std::optional<NecMessage> process_edge(uint32_t now_us, bool pin_level) noexcept {
        const uint32_t delta = now_us - last_time_us_;
        last_time_us_ = now_us;

        switch (state_) {
            case State::Idle:
                if (!pin_level) {
                    state_ = State::LeaderBurst;
                }
                break;

            case State::LeaderBurst:
                if (pin_level) {
                    if (delta >= 7500 && delta <= 10500) {
                        state_ = State::LeaderSpace;
                    } else {
                        state_ = State::Idle;
                    }
                }
                break;

            case State::LeaderSpace:
                if (!pin_level) {
                    if (delta >= 3800 && delta <= 5200) {
                        bit_buffer_ = 0;
                        bit_count_ = 0;
                        state_ = State::DataBit;
                    } else if (delta >= 1800 && delta <= 2700) {
                        state_ = State::Idle;
                        return NecMessage{.is_repeat = true};
                    } else {
                        state_ = State::Idle;
                    }
                }
                break;

            case State::DataBit:
                if (pin_level) {
                    if (delta < 350 || delta > 800) {
                        state_ = State::Idle;
                    }
                } else {
                    if (delta >= 400 && delta <= 750) {
                        ++bit_count_;
                    } else if (delta >= 1400 && delta <= 2000) {
                        bit_buffer_ |= (1UL << bit_count_);
                        ++bit_count_;
                    } else {
                        state_ = State::Idle;
                        break;
                    }

                    if (bit_count_ >= 32) {
                        const auto addr     = static_cast<uint8_t>(bit_buffer_ & 0xFF);
                        const auto addr_inv = static_cast<uint8_t>((bit_buffer_ >> 8) & 0xFF);
                        const auto cmd      = static_cast<uint8_t>((bit_buffer_ >> 16) & 0xFF);
                        const auto cmd_inv  = static_cast<uint8_t>((bit_buffer_ >> 24) & 0xFF);

                        state_ = State::Idle;
                        if ((addr == static_cast<uint8_t>(~addr_inv)) &&
                            (cmd  == static_cast<uint8_t>(~cmd_inv))) {
                            return NecMessage{
                                .address = addr,
                                .command = cmd,
                                .is_repeat = false
                            };
                        }
                    }
                }
                break;
        }
        return std::nullopt;
    }

private:
    State state_{State::Idle};
    uint32_t last_time_us_{0};
    uint32_t bit_buffer_{0};
    uint8_t bit_count_{0};
};

} // namespace optical
