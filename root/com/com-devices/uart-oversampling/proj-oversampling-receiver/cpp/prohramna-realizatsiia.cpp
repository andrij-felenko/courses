#include <cstdint>
#include <array>
#include <optional>
#include <span>
#include <iostream>
#include <iomanip>

enum class OversamplingMode : uint8_t {
    Ratio16x = 16,
    Ratio8x  = 8
};

enum class ReceiverState : uint8_t {
    Idle = 0,
    StartBitVerification,
    DataBitsReception,
    StopBitVerification
};

struct RxFrameResult {
    uint8_t data{0};
    bool    noise_flag{false};
    bool    framing_error{false};
};

template <OversamplingMode Mode = OversamplingMode::Ratio16x>
class UartOversamplingReceiver {
public:
    constexpr UartOversamplingReceiver() noexcept { reset(); }

    void reset() noexcept {
        state_ = ReceiverState::Idle;
        subtick_counter_ = 0;
        bit_index_ = 0;
        shift_reg_ = 0;
        samples_.fill(1);
        prev_rx_pin_ = 1;
        frame_noise_detected_ = false;
        glitch_flag_ = false;
    }

    // Повертає декодований кадр у разі завершення прийому стоп-біта
    std::optional<RxFrameResult> tick(uint8_t rx_pin) noexcept {
        std::optional<RxFrameResult> output_frame = std::nullopt;
        const uint8_t last_tick = static_cast<uint8_t>(Mode) - 1;
        constexpr uint8_t voting_tick = (Mode == OversamplingMode::Ratio16x) ? 9 : 5;

        switch (state_) {
        case ReceiverState::Idle:
            if (prev_rx_pin_ == 1 && rx_pin == 0) { // Спадний фронт
                state_ = ReceiverState::StartBitVerification;
                subtick_counter_ = 0;
                frame_noise_detected_ = false;
                glitch_flag_ = false;
            }
            break;

        case ReceiverState::StartBitVerification:
            recordSample(subtick_counter_, rx_pin);

            if (subtick_counter_ == voting_tick) {
                const auto [start_val, noise] = evaluateMajority();
                if (start_val != 0) { // Хибний старт: завада відфільтрована
                    glitch_flag_ = true;
                    state_ = ReceiverState::Idle;
                    break;
                }
                if (noise) frame_noise_detected_ = true;
            }

            if (subtick_counter_ >= last_tick) {
                subtick_counter_ = 0;
                bit_index_ = 0;
                shift_reg_ = 0;
                state_ = ReceiverState::DataBitsReception;
            } else {
                ++subtick_counter_;
            }
            break;

        case ReceiverState::DataBitsReception:
            recordSample(subtick_counter_, rx_pin);

            if (subtick_counter_ == voting_tick) {
                const auto [bit_val, noise] = evaluateMajority();
                if (noise) frame_noise_detected_ = true;
                shift_reg_ |= static_cast<uint8_t>(bit_val << bit_index_);
            }

            if (subtick_counter_ >= last_tick) {
                subtick_counter_ = 0;
                if (++bit_index_ >= 8) {
                    state_ = ReceiverState::StopBitVerification;
                }
            } else {
                ++subtick_counter_;
            }
            break;

        case ReceiverState::StopBitVerification:
            recordSample(subtick_counter_, rx_pin);

            if (subtick_counter_ == voting_tick) {
                const auto [stop_val, noise] = evaluateMajority();
                if (noise) frame_noise_detected_ = true;

                output_frame = RxFrameResult{
                    .data = shift_reg_,
                    .noise_flag = frame_noise_detected_,
                    .framing_error = (stop_val == 0)
                };
            }

            if (subtick_counter_ >= last_tick) {
                subtick_counter_ = 0;
                state_ = ReceiverState::Idle;
            } else {
                ++subtick_counter_;
            }
            break;
        }

        prev_rx_pin_ = rx_pin;
        return output_frame;
    }

    [[nodiscard]] bool wasGlitchRejected() const noexcept { return glitch_flag_; }

private:
    void recordSample(uint8_t tick, uint8_t pin_level) noexcept {
        if constexpr (Mode == OversamplingMode::Ratio16x) {
            if (tick == 7) samples_[0] = pin_level;
            else if (tick == 8) samples_[1] = pin_level;
            else if (tick == 9) samples_[2] = pin_level;
        } else {
            if (tick == 3) samples_[0] = pin_level;
            else if (tick == 4) samples_[1] = pin_level;
            else if (tick == 5) samples_[2] = pin_level;
        }
    }

    struct MajorityResult {
        uint8_t value;
        bool    noise;
    };

    [[nodiscard]] MajorityResult evaluateMajority() const noexcept {
        const uint8_t sum = samples_[0] + samples_[1] + samples_[2];
        const bool noise = (sum == 1 || sum == 2);
        const uint8_t val = (sum >= 2) ? 1 : 0;
        return {val, noise};
    }

    ReceiverState          state_{ReceiverState::Idle};
    uint8_t                subtick_counter_{0};
    uint8_t                bit_index_{0};
    uint8_t                shift_reg_{0};
    std::array<uint8_t, 3> samples_{1, 1, 1};
    uint8_t                prev_rx_pin_{1};
    bool                   frame_noise_detected_{false};
    bool                   glitch_flag_{false};
};
