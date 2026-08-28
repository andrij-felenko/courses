#include <array>
#include <span>
#include <cstdint>
#include <algorithm>

class CvbsFrameGenerator {
public:
    static constexpr std::size_t SamplesPerLine = 910;
    static constexpr std::size_t ActivePixels   = 739;
    static constexpr std::size_t TotalLines     = 525;

    enum class LineMode { PreEqualizing, VSyncSerrated, PostEqualizing, Blank, Active };

    constexpr CvbsFrameGenerator() noexcept : m_lut(buildLut()) {}

    void renderLine(std::span<std::uint8_t, SamplesPerLine> lineBuffer,
                    std::span<const std::uint8_t> pixelData,
                    std::uint16_t lineIndex) noexcept {
        const std::uint8_t syncDac  = getDacCode(-40);
        const std::uint8_t blankDac = getDacCode(0);

        const LineMode mode = classifyLine(lineIndex);

        if (mode == LineMode::PreEqualizing || mode == LineMode::PostEqualizing) {
            for (std::size_t i = 0; i < SamplesPerLine; ++i) {
                lineBuffer[i] = ((i < 33) || (i >= 455 && i < 488)) ? syncDac : blankDac;
            }
        } else if (mode == LineMode::VSyncSerrated) {
            for (std::size_t i = 0; i < SamplesPerLine; ++i) {
                lineBuffer[i] = ((i < 388) || (i >= 455 && i < 843)) ? syncDac : blankDac;
            }
        } else if (mode == LineMode::Blank) {
            for (std::size_t i = 0; i < SamplesPerLine; ++i) {
                lineBuffer[i] = (i >= 21 && i < 88) ? syncDac : blankDac;
            }
        } else {
            const std::uint8_t phaseOffset = (lineIndex % 2 == 0) ? 2 : 0;
            std::uint8_t burstCounter = 0;

            for (std::size_t i = 0; i < SamplesPerLine; ++i) {
                if (i < 21) {
                    lineBuffer[i] = blankDac;
                } else if (i < 88) {
                    lineBuffer[i] = syncDac;
                } else if (i < 105) {
                    lineBuffer[i] = blankDac;
                } else if (i < 141) {
                    const std::uint8_t p = (burstCounter + phaseOffset) % 4;
                    const std::int16_t burstIre = (p == 1) ? 20 : ((p == 3) ? -20 : 0);
                    lineBuffer[i] = getDacCode(burstIre);
                    ++burstCounter;
                } else if (i < 171) {
                    lineBuffer[i] = blankDac;
                } else {
                    const std::size_t pxIdx = i - 171;
                    const std::uint8_t luma = (pxIdx < pixelData.size()) ? pixelData[pxIdx] : 50;
                    lineBuffer[i] = getDacCode(static_cast<std::int16_t>(luma));
                }
            }
        }
    }

    [[nodiscard]] constexpr std::uint8_t getDacCode(std::int16_t ire) const noexcept {
        const auto idx = static_cast<std::size_t>(std::clamp<std::int16_t>(ire + 40, 0, 140));
        return m_lut[idx];
    }

private:
    std::array<std::uint8_t, 141> m_lut{};

    [[nodiscard]] static constexpr std::array<std::uint8_t, 141> buildLut() noexcept {
        std::array<std::uint8_t, 141> lut{};
        for (std::int16_t i = -40; i <= 100; ++i) {
            const std::int32_t val = ((i + 40) * 255) / 140;
            lut[static_cast<std::size_t>(i + 40)] = static_cast<std::uint8_t>(std::clamp(val, 0, 255));
        }
        return lut;
    }

    [[nodiscard]] static constexpr LineMode classifyLine(std::uint16_t line) noexcept {
        if ((line >= 1 && line <= 3) || (line >= 264 && line <= 266)) return LineMode::PreEqualizing;
        if ((line >= 4 && line <= 6) || (line >= 267 && line <= 269)) return LineMode::VSyncSerrated;
        if ((line >= 7 && line <= 9) || (line >= 270 && line <= 272)) return LineMode::PostEqualizing;
        if ((line >= 10 && line <= 21) || (line >= 273 && line <= 284)) return LineMode::Blank;
        return LineMode::Active;
    }
};
