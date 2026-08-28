#include <iostream>
#include <iomanip>
#include <string_view>
#include <expected>
#include <format>

enum class DielectricMaterial {
    PcbMicrostrip,  // ~5.96 ns/m
    PcbStripline,   // ~6.91 ns/m
    RibbonCablePvc, // ~5.48 ns/m
    TwistedPairPe   // ~5.00 ns/m
};

struct MasterTimingProfile {
    double setupTimeNs{4.5};
    double holdTimeNs{2.0};
    double clockToOutputNs{6.0};
    double clockSkewNs{1.0};
    bool enableSampleShift{false};
};

struct SlaveTimingProfile {
    double setupTimeNs{3.0};
    double holdTimeNs{2.0};
    double outputValidMaxNs{8.0};
    double outputValidMinNs{1.5};
};

struct ChannelTopology {
    double lengthMeters{0.25};
    DielectricMaterial material{DielectricMaterial::RibbonCablePvc};
    double isolatorDelayNs{10.7};
    double riseTimeNs{3.0};

    [[nodiscard]] constexpr double unitPropagationDelayNsPerM() const noexcept {
        switch (material) {
            case DielectricMaterial::PcbMicrostrip:  return 5.96;
            case DielectricMaterial::PcbStripline:   return 6.91;
            case DielectricMaterial::RibbonCablePvc: return 5.48;
            case DielectricMaterial::TwistedPairPe:   return 5.00;
        }
        return 6.00;
    }
};

struct TimingAnalysisReport {
    double frequencyMhz;
    double periodNs;
    double singleWirePropDelayNs;
    double activeIsolatorDelayNs;
    double roundTripDelayNs;

    double writeSetupMarginNs;
    double readSetupMarginNs;
    double readHoldMarginNs;

    double maxFrequencyWriteMhz;
    double maxFrequencyReadStandardMhz;
    double maxFrequencyReadShiftedMhz;

    [[nodiscard]] constexpr bool isWriteValid() const noexcept { return writeSetupMarginNs >= 0.0; }
    [[nodiscard]] constexpr bool isReadValid() const noexcept { return readSetupMarginNs >= 0.0; }
    [[nodiscard]] constexpr bool isHoldValid() const noexcept { return readHoldMarginNs >= 0.0; }
    [[nodiscard]] constexpr bool isFullyCompliant() const noexcept {
        return isWriteValid() && isReadValid() && isHoldValid();
    }
};

enum class AnalysisError {
    InvalidFrequency,
    NegativeLength,
    InvalidParameters
};

class SpiTimingEngine {
public:
    [[nodiscard]] static std::expected<TimingAnalysisReport, AnalysisError> evaluate(
        const MasterTimingProfile& master,
        const SlaveTimingProfile& slave,
        const ChannelTopology& channel,
        double targetFrequencyMhz
    ) noexcept {
        if (targetFrequencyMhz <= 0.0) return std::unexpected(AnalysisError::InvalidFrequency);
        if (channel.lengthMeters < 0.0) return std::unexpected(AnalysisError::NegativeLength);

        TimingAnalysisReport report{};
        report.frequencyMhz = targetFrequencyMhz;
        report.periodNs = 1000.0 / targetFrequencyMhz;
        const double halfPeriodNs = report.periodNs / 2.0;

        report.singleWirePropDelayNs = channel.lengthMeters * channel.unitPropagationDelayNsPerM();
        report.activeIsolatorDelayNs = channel.isolatorDelayNs * 2.0; // SCLK + MISO
        report.roundTripDelayNs = (2.0 * report.singleWirePropDelayNs) + 
                                  report.activeIsolatorDelayNs + 
                                  slave.outputValidMaxNs;

        // 1. Write Path
        const double writeArrivalNs = master.clockToOutputNs + report.singleWirePropDelayNs + 
                                      channel.isolatorDelayNs + master.clockSkewNs;
        report.writeSetupMarginNs = halfPeriodNs - writeArrivalNs - slave.setupTimeNs;
        report.maxFrequencyWriteMhz = 1000.0 / (2.0 * (writeArrivalNs + slave.setupTimeNs));

        // 2. Read Path Setup
        if (master.enableSampleShift) {
            report.readSetupMarginNs = report.periodNs - report.roundTripDelayNs - master.setupTimeNs;
        } else {
            report.readSetupMarginNs = halfPeriodNs - report.roundTripDelayNs - master.setupTimeNs;
        }

        // 3. Read Path Hold
        const double holdArrivalNs = (2.0 * report.singleWirePropDelayNs) + 
                                     report.activeIsolatorDelayNs + 
                                     slave.outputValidMinNs;
        report.readHoldMarginNs = holdArrivalNs - master.holdTimeNs;

        // Boundary Frequencies
        report.maxFrequencyReadStandardMhz = 1000.0 / (2.0 * (report.roundTripDelayNs + master.setupTimeNs));
        report.maxFrequencyReadShiftedMhz = 1000.0 / (report.roundTripDelayNs + master.setupTimeNs);

        return report;
    }

    static void printConsoleReport(const TimingAnalysisReport& r) {
        std::cout << std::string(65, '=') << '\n';
        std::cout << "           ЗВІТ ЧАСОВОГО БАЛАНСУ ШИНИ SPI (C++20)\n";
        std::cout << std::string(65, '=') << '\n';
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "Цільова частота шини         : " << r.frequencyMhz << " МГц\n";
        std::cout << "Період тактового імпульсу    : " << r.periodNs << " нс\n";
        std::cout << "Затримка провідника (в 1 бік): " << r.singleWirePropDelayNs << " нс\n";
        std::cout << "Затримка пари ізоляторів     : " << r.activeIsolatorDelayNs << " нс\n";
        std::cout << "Повна затримка кругового руху: " << r.roundTripDelayNs << " нс\n";
        std::cout << std::string(65, '-') << '\n';
        
        std::cout << "ТРАКТ ЗАПИСУ (MOSI):\n";
        std::cout << "  Запас Setup : " << std::showpos << r.writeSetupMarginNs 
                  << " нс [" << (r.isWriteValid() ? "OK" : "VIOLATION") << "]\n";
        std::cout << std::noshowpos;
        std::cout << "  Стеля запису: " << r.maxFrequencyWriteMhz << " МГц\n";
        std::cout << std::string(65, '-') << '\n';

        std::cout << "ТРАКТ ЧИТАННЯ (MISO):\n";
        std::cout << "  Запас Setup : " << std::showpos << r.readSetupMarginNs 
                  << " нс [" << (r.isReadValid() ? "OK" : "VIOLATION") << "]\n";
        std::cout << "  Запас Hold  : " << r.readHoldMarginNs 
                  << " нс [" << (r.isHoldValid() ? "OK" : "VIOLATION") << "]\n";
        std::cout << std::noshowpos;
        std::cout << "  Стеля читання (стандарт CPHA=0): " << r.maxFrequencyReadStandardMhz << " МГц\n";
        std::cout << "  Стеля читання (Sample Shift)   : " << r.maxFrequencyReadShiftedMhz << " МГц\n";
        std::cout << std::string(65, '=') << '\n';
    }
};

int main() {
    const MasterTimingProfile stm32{};
    const SlaveTimingProfile flash{};
    const ChannelTopology channel{
        .lengthMeters = 0.25,
        .material = DielectricMaterial::RibbonCablePvc,
        .isolatorDelayNs = 10.7,
        .riseTimeNs = 3.0
    };

    auto result = SpiTimingEngine::evaluate(stm32, flash, channel, 20.0);
    if (result) {
        SpiTimingEngine::printConsoleReport(*result);
    } else {
        std::cerr << "Помилка аналізу часових параметрів\n";
    }

    return 0;
}
