// Об'єктно-орієнтована конфігурація вибору чипсета та шини в C++
#include <cstdint>

enum class ChipsetType {
    WS2812B,
    SK6812_RGBW,
    APA102,
    WS2815
};

class LedStripDescriptor {
public:
    constexpr LedStripDescriptor(ChipsetType type, uint16_t pixelCount) noexcept
        : type_(type), pixelCount_(pixelCount) {}

    [[nodiscard]] constexpr uint8_t colorChannels() const noexcept {
        return (type_ == ChipsetType::SK6812_RGBW) ? 4 : 3;
    }

    [[nodiscard]] constexpr bool requiresClock() const noexcept {
        return type_ == ChipsetType::APA102;
    }

    [[nodiscard]] constexpr bool hasRedundancy() const noexcept {
        return type_ == ChipsetType::WS2815;
    }

    [[nodiscard]] constexpr uint32_t maxBusSpeedHz() const noexcept {
        return (type_ == ChipsetType::APA102) ? 24000000UL : 800000UL;
    }

private:
    ChipsetType type_;
    uint16_t pixelCount_;
};
