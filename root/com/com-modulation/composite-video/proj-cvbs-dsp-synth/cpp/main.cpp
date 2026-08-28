#include <cstdint>
#include <vector>
#include <array>
#include <cmath>
#include <numbers>
#include <span>
#include <algorithm>

class PalCvbsSynthesizer {
public:
    static constexpr double SampleRateHz = 17734475.0;
    static constexpr std::size_t LineSamples = 1135;
    static constexpr double SubcarrierFreqHz = 4433618.75;

    static constexpr uint8_t DacSyncTip   = 0;
    static constexpr uint8_t DacBlanking  = 73;
    static constexpr uint8_t DacWhite100  = 255;
    static constexpr double  DacBurstAmp  = 36.0;

    struct ColorBar {
        float yNorm;
        float uNorm;
        float vNorm;
    };

    static constexpr std::array<ColorBar, 8> EbuBars {{
        { 0.75f,  0.000f,  0.000f }, // Білий 75%
        { 0.64f, -0.327f,  0.075f }, // Жовтий
        { 0.53f,  0.110f, -0.461f }, // Ціан
        { 0.41f, -0.217f, -0.386f }, // Зелений
        { 0.34f,  0.217f,  0.386f }, // Пурпур
        { 0.23f, -0.110f,  0.461f }, // Червоний
        { 0.11f,  0.327f, -0.075f }, // Синій
        { 0.00f,  0.000f,  0.000f }  // Чорний
    }};

    void generateLine(std::span<uint8_t, LineSamples> buffer, std::uint32_t lineNumber) const {
        const bool isVInverted = (lineNumber % 2 != 0);
        const double omegaSc = 2.0 * std::numbers::pi * SubcarrierFreqHz / SampleRateHz;
        const double burstPhaseOffset = isVInverted ? (3.0 * std::numbers::pi / 4.0) : (-3.0 * std::numbers::pi / 4.0);

        constexpr std::size_t SyncStart   = 27;
        constexpr std::size_t SyncEnd     = 110;
        constexpr std::size_t BurstStart  = 126;
        constexpr std::size_t BurstEnd    = 170;
        constexpr std::size_t ActiveStart = 213;

        for (std::size_t i = 0; i < LineSamples; ++i) {
            if (i < SyncStart) {
                buffer[i] = DacBlanking;
            } else if (i < SyncEnd) {
                buffer[i] = DacSyncTip;
            } else if (i < BurstStart) {
                buffer[i] = DacBlanking;
            } else if (i < BurstEnd) {
                const double burstVal = DacBurstAmp * std::sin(omegaSc * static_cast<double>(i) + burstPhaseOffset);
                buffer[i] = clampDac(static_cast<int32_t>(DacBlanking + burstVal + 0.5));
            } else if (i < ActiveStart) {
                buffer[i] = DacBlanking;
            } else {
                const std::size_t activeIdx = i - ActiveStart;
                const std::size_t barWidth = (LineSamples - ActiveStart) / 8;
                const std::size_t barIdx = std::min(activeIdx / barWidth, std::size_t{7});

                const auto& bar = EbuBars[barIdx];
                const double yDac = DacBlanking + bar.yNorm * (DacWhite100 - DacBlanking);

                const double vSign = isVInverted ? -1.0 : 1.0;
                const double uMod = bar.uNorm * std::sin(omegaSc * static_cast<double>(i));
                const double vMod = vSign * bar.vNorm * std::cos(omegaSc * static_cast<double>(i));
                const double chromaDac = (uMod + vMod) * (DacWhite100 - DacBlanking);

                buffer[i] = clampDac(static_cast<int32_t>(yDac + chromaDac + 0.5));
            }
        }
    }

private:
    static constexpr uint8_t clampDac(int32_t value) noexcept {
        return static_cast<uint8_t>(std::clamp(value, int32_t{0}, int32_t{255}));
    }
};
