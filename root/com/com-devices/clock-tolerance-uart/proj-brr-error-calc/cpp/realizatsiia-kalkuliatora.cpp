#include <iostream>
#include <iomanip>
#include <cmath>
#include <cstdint>
#include <optional>
#include <string_view>

namespace uart_tools {

enum class ClockSource {
    CrystalXtal,    // Кварцовий резонатор (±30..50 ppm)
    CeramicRes,     // Керамічний резонатор (±0.5%)
    InternalRc      // Внутрішній RC-генератор (±2.5%)
};

enum class FrameFormat {
    Frame8N1,           // 10 бітів: Start, 8 Data, Stop
    Frame8E1_8O1_8N2,   // 11 бітів: Start, 8 Data, Parity, Stop
    Frame9E1            // 12 бітів: Start, 9 Data, Parity, Stop
};

struct CalculationConfig {
    uint32_t pclkHz{16'000'000};
    uint32_t targetBaud{115'200};
    uint32_t oversampling{16};
    uint32_t fractBits{4};
    ClockSource txClock{ClockSource::InternalRc};
    ClockSource rxClock{ClockSource::CrystalXtal};
    FrameFormat format{FrameFormat::Frame8N1};
};

struct BaudRateResult {
    uint32_t mantissa{0};
    uint32_t fraction{0};
    uint32_t rawRegisterValue{0};
    double actualBaud{0.0};
    double quantizationErrorPercent{0.0};
    double totalSystemErrorPercent{0.0};
    double maxAllowableErrorPercent{0.0};
    bool isReliable{false};
};

class BaudRateCalculator {
public:
    [[nodiscard]] static constexpr double getClockDriftPercent(ClockSource source) noexcept {
        switch (source) {
            case ClockSource::CrystalXtal: return 0.005; // ±50 ppm
            case ClockSource::CeramicRes:  return 0.500; // ±0.5%
            case ClockSource::InternalRc:  return 2.500; // ±2.5%
        }
        return 1.0;
    }

    [[nodiscard]] static constexpr double getMaxAllowableError(FrameFormat format, uint32_t oversampling) noexcept {
        const double nBits = [format]() {
            switch (format) {
                case FrameFormat::Frame8N1:         return 10.0;
                case FrameFormat::Frame8E1_8O1_8N2: return 11.0;
                case FrameFormat::Frame9E1:         return 12.0;
            }
            return 10.0;
        }();

        const double wEff = (oversampling == 16) ? 0.40625 : 0.31250;
        return (wEff / (nBits - 0.5)) * 100.0;
    }

    [[nodiscard]] static std::optional<BaudRateResult> calculate(const CalculationConfig& cfg) noexcept {
        if (cfg.pclkHz == 0 || cfg.targetBaud == 0) {
            return std::nullopt;
        }
        if (cfg.oversampling != 8 && cfg.oversampling != 16) {
            return std::nullopt;
        }

        const double divExact = static_cast<double>(cfg.pclkHz) /
                                (static_cast<double>(cfg.oversampling) * static_cast<double>(cfg.targetBaud));
        if (divExact < 1.0) {
            return std::nullopt;
        }

        const uint32_t fractScale = 1u << cfg.fractBits;
        const auto divScaled = static_cast<uint32_t>(std::round(divExact * static_cast<double>(fractScale)));

        BaudRateResult res;
        res.mantissa = divScaled >> cfg.fractBits;
        res.fraction = divScaled & (fractScale - 1u);

        if (res.mantissa == 0) {
            return std::nullopt;
        }

        res.rawRegisterValue = (res.mantissa << cfg.fractBits) | res.fraction;

        const double divActual = static_cast<double>(res.mantissa) +
                                 (static_cast<double>(res.fraction) / static_cast<double>(fractScale));
        res.actualBaud = static_cast<double>(cfg.pclkHz) / (static_cast<double>(cfg.oversampling) * divActual);
        res.quantizationErrorPercent = ((res.actualBaud - static_cast<double>(cfg.targetBaud)) /
                                        static_cast<double>(cfg.targetBaud)) * 100.0;

        const double txDrift = getClockDriftPercent(cfg.txClock);
        const double rxDrift = getClockDriftPercent(cfg.rxClock);

        res.totalSystemErrorPercent = std::abs(res.quantizationErrorPercent) + txDrift + rxDrift;
        res.maxAllowableErrorPercent = getMaxAllowableError(cfg.format, cfg.oversampling);
        res.isReliable = (res.totalSystemErrorPercent <= res.maxAllowableErrorPercent);

        return res;
    }

    static void printReport(const CalculationConfig& cfg, const BaudRateResult& res) {
        std::cout << "============================================================\n";
        std::cout << " ЗВІТ РОЗРАХУНКУ ТАКТУВАННЯ ТА БЮДЖЕТУ ПОХИБКИ UART (C++)\n";
        std::cout << "============================================================\n";
        std::cout << std::fixed << std::setprecision(3);
        std::cout << " Тактова частота PCLK     : " << cfg.pclkHz << " Гц (" << (cfg.pclkHz / 1e6) << " МГц)\n";
        std::cout << " Цільова швидкість (Baud) : " << cfg.targetBaud << " бод\n";
        std::cout << " Мантиса дільника         : " << res.mantissa << "\n";
        std::cout << " Дробова частина          : " << res.fraction << " / 16\n";
        std::cout << " Регістр USART_BRR        : 0x" << std::hex << std::uppercase << res.rawRegisterValue << std::dec << "\n";
        std::cout << std::setprecision(2);
        std::cout << " Фактична швидкість       : " << res.actualBaud << " бод\n";
        std::cout << std::setprecision(3);
        std::cout << " Похибка дільника BRR     : " << std::showpos << res.quantizationErrorPercent << " %\n" << std::noshowpos;
        std::cout << " Сумарна похибка системи  : " << res.totalSystemErrorPercent << " %\n";
        std::cout << " Гранично допустима межа  : " << res.maxAllowableErrorPercent << " %\n";
        std::cout << "------------------------------------------------------------\n";
        if (res.isReliable) {
            std::cout << " ВЕРДИКТ: [ НАДІЙНО ] Зв'язок гарантовано стабільний.\n";
        } else {
            std::cout << " ВЕРДИКТ: [ НЕБЕЗПЕКА ] Ризик Framing Error! Перевищено допуск.\n";
        }
        std::cout << "============================================================\n\n";
    }
};

} // namespace uart_tools
