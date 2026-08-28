#include <array>
#include <cstdint>

template <size_t PinCount>
class CharlieplexDriver {
public:
    static constexpr size_t LedCount = PinCount * (PinCount - 1);

    struct PinPair {
        uint8_t anode;
        uint8_t cathode;
    };

    struct GpioInterface {
        void (*setHiZ)(uint8_t pin);
        void (*setHigh)(uint8_t pin);
        void (*setLow)(uint8_t pin);
    };

    explicit CharlieplexDriver(GpioInterface gpio) noexcept
        : gpio_(gpio), currentSlot_(0), buffer_{} {}

    void setPixel(size_t index, bool state) noexcept {
        if (index < LedCount) {
            buffer_[index] = state;
        }
    }

    void clear() noexcept {
        buffer_.fill(false);
    }

    /* Виклик у періодичному перериванні таймера */
    void handleInterrupt() noexcept {
        for (uint8_t i = 0; i < PinCount; ++i) {
            gpio_.setHiZ(i);
        }

        if (buffer_[currentSlot_]) {
            const auto pair = getPair(currentSlot_);
            gpio_.setHigh(pair.anode);
            gpio_.setLow(pair.cathode);
        }

        currentSlot_ = (currentSlot_ + 1) % LedCount;
    }

    [[nodiscard]] static constexpr PinPair getPair(size_t slot) noexcept {
        size_t idx = 0;
        for (uint8_t a = 0; a < PinCount; ++a) {
            for (uint8_t c = 0; c < PinCount; ++c) {
                if (a != c) {
                    if (idx == slot) return {a, c};
                    idx++;
                }
            }
        }
        return {0, 0};
    }

private:
    GpioInterface gpio_;
    size_t currentSlot_;
    std::array<bool, LedCount> buffer_;
};
