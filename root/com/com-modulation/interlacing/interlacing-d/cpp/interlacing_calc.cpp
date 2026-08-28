// interlacing_calc.cpp — обчислення полів та анти-твіттер фільтр на C++
#include <iostream>
#include <vector>
#include <cstdint>
#include <span>

struct VideoTiming {
    float lineTimeUs;
    float activeVideoUs;
    uint32_t totalPixelsPerLine;
};

class InterlacingProcessor {
public:
    static constexpr uint32_t PalLines = 625;
    static constexpr float PalFieldRate = 50.0f;
    static constexpr size_t Width = 720;
    static constexpr size_t Height = 576;

    static constexpr VideoTiming computePalTiming(float pixelClockMhz) noexcept {
        const float lineRate = (PalLines / 2.0f) * PalFieldRate;
        const float lineTimeUs = (1.0f / lineRate) * 1.0e6f;
        const float activeVideoUs = 52.0f;
        const uint32_t totalPixels = static_cast<uint32_t>(pixelClockMhz * activeVideoUs);
        return VideoTiming{lineTimeUs, activeVideoUs, totalPixels};
    }

    // Anti-Twitter фільтр з використанням std::span для безпечного доступу до пам'яті
    static void applyAntiTwitterFilter(std::span<uint8_t> frameBuffer) {
        if (frameBuffer.size() < Width * Height) return;

        for (size_t y = 1; y < Height - 1; ++y) {
            for (size_t x = 0; x < Width; ++x) {
                const size_t currIdx = y * Width + x;
                const size_t topIdx  = (y - 1) * Width + x;
                const size_t botIdx  = (y + 1) * Width + x;

                const uint16_t val = static_cast<uint16_t>(frameBuffer[topIdx]) +
                                     2 * static_cast<uint16_t>(frameBuffer[currIdx]) +
                                     static_cast<uint16_t>(frameBuffer[botIdx]);

                frameBuffer[currIdx] = static_cast<uint8_t>(val / 4);
            }
        }
    }
};
