#include <cstdint>
#include <vector>
#include <array>
#include <cmath>
#include <numbers>
#include <span>
#include <algorithm>

class PalVideoLineGenerator {
public:
    static constexpr double SampleRateHz   = 17734475.0;
    static constexpr std::size_t LineSize = 1135;
    static constexpr double SubcarrierHz  = 4433618.75;

    static constexpr uint8_t DacSyncTip   = 0;
    static constexpr uint8_t DacBlanking  = 73;
    static constexpr uint8_t DacWhite100  = 255;
    static constexpr double  DacBurstAmp  = 36.0;

    struct ColorBarSpec {
        float luma;
        float chromaU;
        float chromaV;
    };

    static constexpr std::array<ColorBarSpec, 8> ColorBars75 {{
        { 0.75f,  0.000f,  0.000f }, // 75% White
        { 0.64f, -0.327f,  0.075f }, // Yellow
        { 0.53f,  0.110f, -0.461f }, // Cyan
        { 0.41f, -0.217f, -0.386f }, // Green
        { 0.34f,  0.217f,  0.386f }, // Magenta
        { 0.23f, -0.110f,  0.461f }, // Red
        { 0.11f,  0.327f, -0.075f }, // Blue
        { 0.00f,  0.000f,  0.000f }  // Black
    }};

    void generateScanline(std::span<uint8_t, LineSize> outBuffer, std::uint32_t lineIdx) const {
        const bool vInvert = (lineIdx % 2 != 0);
        const double omega = 2.0 * std::numbers::pi * SubcarrierHz / SampleRateHz;
        const double burstPhase = vInvert ? (3.0 * std::numbers::pi / 4.0) : (-3.0 * std::numbers::pi / 4.0);

        constexpr std::size_t PosSyncStart  = 27;
        constexpr std::size_t PosSyncEnd    = 110;
        constexpr std::size_t PosBurstStart = 126;
        constexpr std::size_t PosBurstEnd   = 170;
        constexpr std::size_t PosActive     = 213;

        for (std::size_t i = 0; i < LineSize; ++i) {
            if (i < PosSyncStart) {
                outBuffer[i] = DacBlanking;
            } else if (i < PosSyncEnd) {
                outBuffer[i] = DacSyncTip;
            } else if (i < PosBurstStart) {
                outBuffer[i] = DacBlanking;
            } else if (i < PosBurstEnd) {
                const double burst = DacBurstAmp * std::sin(omega * static_cast<double>(i) + burstPhase);
                outBuffer[i] = clampSample(static_cast<int32_t>(DacBlanking + burst + 0.5));
            } else if (i < PosActive) {
                outBuffer[i] = DacBlanking;
            } else {
                const std::size_t actI = i - PosActive;
                const std::size_t barW = (LineSize - PosActive) / 8;
                const std::size_t barI = std::min(actI / barW, std::size_t{7});

                const auto& bar = ColorBars75[barI];
                const double y = DacBlanking + bar.luma * (DacWhite100 - DacBlanking);

                const double vFactor = vInvert ? -1.0 : 1.0;
                const double uMod = bar.chromaU * std::sin(omega * static_cast<double>(i));
                const double vMod = vFactor * bar.chromaV * std::cos(omega * static_cast<double>(i));
                const double c = (uMod + vMod) * (DacWhite100 - DacBlanking);

                outBuffer[i] = clampSample(static_cast<int32_t>(y + c + 0.5));
            }
        }
    }

private:
    static constexpr uint8_t clampSample(int32_t val) noexcept {
        return static_cast<uint8_t>(std::clamp(val, int32_t{0}, int32_t{255}));
    }
};
