#include <cstdint>
#include <array>

namespace hw {

class RotaryEncoder {
public:
    enum class StepResolution : uint8_t {
        FullCycle = 4,  // 4 зміни стану на один тактильний клік (detent)
        HalfCycle = 2,  // 2 зміни стану на один тактильний клік
        QuarterStep = 1 // Реагувати на кожен фронт (максимальна роздільність)
    };

    constexpr explicit RotaryEncoder(StepResolution resolution = StepResolution::FullCycle) noexcept
        : resolution_(static_cast<int8_t>(resolution)) {}

    void init(bool initial_a, bool initial_b) noexcept {
        prevState_ = static_cast<uint8_t>((static_cast<uint8_t>(initial_a) << 1) | 
                                          static_cast<uint8_t>(initial_b));
        subCount_ = 0;
        position_ = 0;
    }

    // Викликається з періодичного таймера (1 кГц)
    void update(bool raw_a, bool raw_b) noexcept {
        const uint8_t currState = static_cast<uint8_t>((static_cast<uint8_t>(raw_a) << 1) | 
                                                       static_cast<uint8_t>(raw_b));
        const uint8_t index = static_cast<uint8_t>((prevState_ << 2) | currState);
        const int8_t delta = transitionTable_[index & 0x0F];

        prevState_ = currState;

        if (delta != 0) {
            subCount_ += delta;
            if (subCount_ >= resolution_) {
                position_ += (subCount_ / resolution_);
                subCount_ %= resolution_;
            } else if (subCount_ <= -resolution_) {
                position_ += (subCount_ / resolution_);
                subCount_ %= resolution_;
            }
        }
    }

    [[nodiscard]] constexpr int32_t position() const noexcept { return position_; }
    void setPosition(int32_t newPos) noexcept { position_ = newPos; subCount_ = 0; }

private:
    static constexpr std::array<int8_t, 16> transitionTable_ = {
        0,  1, -1,  0,
       -1,  0,  0,  1,
        1,  0,  0, -1,
        0, -1,  1,  0
    };

    uint8_t prevState_{0};
    int8_t subCount_{0};
    int8_t resolution_{4};
    int32_t position_{0};
};

} // namespace hw
