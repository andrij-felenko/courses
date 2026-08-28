#include <array>
#include <span>
#include <cstdint>
#include <algorithm>

template <size_t PinCount>
class CharlieplexMatrix {
public:
    static constexpr size_t LedCount = PinCount * (PinCount - 1);
    static constexpr uint8_t MaxBrightness = 7;

    struct LedPinPair {
        uint8_t anode;
        uint8_t cathode;
    };

    struct HardwarePort {
        void (*setHigh)(uint8_t pin);
        void (*setLow)(uint8_t pin);
        void (*setHiZ)(uint8_t pin);
    };

    explicit constexpr CharlieplexMatrix(HardwarePort hal) noexcept
        : hal_(hal), currentLed_(0), pwmCounter_(0), brightness_{} {}

    void init() const noexcept {
        for (uint8_t i = 0; i < PinCount; ++i) {
            hal_.setHiZ(i);
        }
    }

    void setBrightness(size_t ledIndex, uint8_t level) noexcept {
        if (ledIndex < LedCount) {
            brightness_[ledIndex] = std::min(level, MaxBrightness);
        }
    }

    void fill(uint8_t level) noexcept {
        brightness_.fill(std::min(level, MaxBrightness));
    }

    /* Виклик у періодичному перериванні таймера */
    void tick() noexcept {
        /* Фаза мертвого часу (dead-time): гарантовано ізолюємо всі виводи */
        for (uint8_t i = 0; i < PinCount; ++i) {
            hal_.setHiZ(i);
        }

        const size_t led = currentLed_;
        if (brightness_[led] > pwmCounter_) {
            const auto pair = computeLedPair(led);
            hal_.setHigh(pair.anode);
            hal_.setLow(pair.cathode);
        }

        currentLed_ = (currentLed_ + 1) % LedCount;
        if (currentLed_ == 0) {
            pwmCounter_ = (pwmCounter_ + 1) % (MaxBrightness + 1);
        }
    }

    [[nodiscard]] static constexpr LedPinPair computeLedPair(size_t index) noexcept {
        size_t count = 0;
        for (uint8_t a = 0; a < PinCount; ++a) {
            for (uint8_t c = 0; c < PinCount; ++c) {
                if (a != c) {
                    if (count == index) return {a, c};
                    count++;
                }
            }
        }
        return {0, 0};
    }

private:
    HardwarePort hal_;
    size_t currentLed_;
    uint8_t pwmCounter_;
    std::array<uint8_t, LedCount> brightness_;
};
