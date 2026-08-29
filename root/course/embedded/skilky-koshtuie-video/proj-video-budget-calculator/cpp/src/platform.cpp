#include "video/platform.hpp"

#include <array>

namespace video {
namespace {

// Кілька типових точок на шкалі «мікроконтролер — Linux SoC».
// Пропускна здатність практична, приблизно половина пікової.
constexpr std::array kPlatforms{
    Platform{"ESP32-S3, PSRAM 8 MB (OctoSPI)",         55.0,    8.0},
    Platform{"STM32H7, AXI SRAM 0.5 MB",              800.0,    0.5},
    Platform{"STM32H7 + HyperRAM 32 MB (x8 DDR)",     180.0,   32.0},
    Platform{"SoC + DDR3-1066 x16, 128 MB",          1000.0,  128.0},
    Platform{"SoC + LPDDR4 x32, 512 MB",             6000.0,  512.0},
};

}  // namespace

std::span<const Platform> catalogue() noexcept
{
    return kPlatforms;
}

FitReport check(const Platform& platform, const Budget& budget) noexcept
{
    FitReport report{};
    report.busLoadPercent = budget.dramMBps  / platform.busMBps * 100.0;
    report.ramLoadPercent = budget.ramPoolMB / platform.ramMB   * 100.0;

    // Пам'ять судимо першою: коли буфери не вміщуються, розмова про шину вже
    // безпредметна — конвеєр не запуститься взагалі.
    if (report.ramLoadPercent > 100.0)
        report.verdict = Fit::NotEnoughRam;
    else if (report.busLoadPercent > 100.0)
        report.verdict = Fit::BusOverload;
    else if (report.busLoadPercent > kBusSafePercent)
        report.verdict = Fit::Risky;
    else
        report.verdict = Fit::Ok;

    return report;
}

std::string_view describe(Fit fit) noexcept
{
    switch (fit) {
        case Fit::Ok:           return "запас є";
        case Fit::Risky:        return "на межі: понад 60 % шини, зриви FIFO на піках";
        case Fit::BusOverload:  return "шина не тягне";
        case Fit::NotEnoughRam: return "бракує пам'яті під кадрові буфери";
    }
    return "?";
}

}  // namespace video
